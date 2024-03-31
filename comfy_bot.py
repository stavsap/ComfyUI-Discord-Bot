import asyncio
import os
import io
import discord
from discord import File
from discord.ext import commands
import uuid
from discord.ui import View, Button

from bot_db import BotDB
from comfy_handlers_manager import ComfyHandlersManager, ComfyHandlersContext
from comfy_client import ComfyClient, QueuePromptResult
from common import get_logger

intents = discord.Intents.default()
intents.dm_messages = True
bot = commands.Bot(intents=intents, command_prefix="/")
logger = get_logger("ComfyBOT")


def process_message(message):
    # TODO optimize by finding the hash tags and replace only them
    # hashtag_pattern = r'#\w+'
    # hashtags = re.findall(hashtag_pattern, message)

    prefix = ComfyHandlersContext().get_prefix(ComfyHandlersManager().get_current_handler().key())
    postfix = ComfyHandlersContext().get_postfix(ComfyHandlersManager().get_current_handler().key())
    if prefix is not None:
        message = "{} {}".format(prefix, message)
    if postfix is not None:
        message = "{} {}".format(message, postfix)

    refs = ComfyHandlersContext().get_reference(ComfyHandlersManager().get_current_handler().key())
    message = message + " "
    for key, value in refs.items():
        message = message.replace("{} ".format(key), "{} ".format(value))
    message = message[:-1]
    logger.debug("processed prompt: {}".format(message))
    return message


# Event triggered when the bot is ready
@bot.event
async def on_ready():
    logger.info(f'on_ready - logged in as {bot.user.name} bot.')


@bot.event
async def on_message(message):
    # Check if the message is from a user and not the bot itself
    if message.author == bot.user:
        return
    #
    # print(str(len(message.attachments)))
    # print(message.attachments[0].content_type)

    if len(message.attachments) > 0:
        for attachment in message.attachments:
            ans =""
            if attachment.content_type.startswith('image'):
                ans = "{}\n<{}>".format(ans, attachment.url)
            if len(ans) > 0:
                await message.channel.send(ans)

    if message.content.startswith("!help"):
        await message.channel.send("Hi, use '/' commands")
    # Check if the message starts with a specific command or trigger
    # async def rerun(interaction):
    #     print(interaction.custom_id)
    #     await interaction.response.send_message("")
    #
    # view = View()
    # btn = Button(label="Again!", style=discord.ButtonStyle.green, custom_id="test_button")
    # btn.callback = rerun
    # view.add_item(btn)
    # await message.channel.send("", view=view)

    # # Open the image file
    # with open("example.png", "rb") as f:
    #     picture = discord.File(f)
    #
    # # Send the message with the picture attached
    # await message.channel.send("Here's a picture!", file=picture)


queue_prompt_results: QueuePromptResult = []


def handle_queue_prompt_result(ctx, p, prompt_handler, res: QueuePromptResult):
    res.ctx = ctx
    res.prompt = p
    res.prompt_handler = prompt_handler
    queue_prompt_results.append(res)


async def publish_images():
    while True:
        await asyncio.sleep(1)
        if len(queue_prompt_results) > 0:
            await handle_prompt_queue_result(queue_prompt_results.pop(0))


bot.loop.create_task(publish_images())


async def handle_prompt_queue_result(queue_prompt_result: QueuePromptResult):
    prompt_id = queue_prompt_result.prompt_id
    ctx = queue_prompt_result.ctx
    images = queue_prompt_result.images
    prompt_handler = queue_prompt_result.prompt_handler
    await ctx.respond("Completed prompt: {}\n{}".format(prompt_id, prompt_handler.describe(queue_prompt_result.prompt)))
    for node_id, image_list in images.items():
        imgs = [File(filename=str(uuid.uuid4()) + ".png", fp=io.BytesIO(image_data)) for image_data in image_list]
        for img in imgs:
            await ctx.respond("", file=img)


@bot.slash_command(name="q", description="Submit a prompt to current workflow handler")
async def q(ctx: discord.commands.context.ApplicationContext, message):
    prompt_handler = ComfyHandlersManager().get_current_handler()
    p = prompt_handler.handle(process_message(message))
    await ctx.defer()
    ComfyClient().queue_prompt(p, lambda res: handle_queue_prompt_result(ctx, p, prompt_handler, res))


@bot.slash_command(name="ref-set", description="Set a reference value")
async def ref_set(ctx, ref, value):
    if '#' in ref:
        await ctx.respond("\# can`t be in the given ref name!")
        return
    if ' ' in ref:
        await ctx.respond("white space can`t be in the given ref name!")
        return
    ComfyHandlersContext().set_reference(ComfyHandlersManager().get_current_handler().key(), ref, value)
    await ctx.respond("Set #{}={}".format(ref, value))


@bot.slash_command(name="ref-del", description="Remove a reference")
async def ref_del(ctx, ref):
    if '#' in ref:
        await ctx.respond('\# can`t be in the given ref name!')
        return
    if ' ' in ref:
        await ctx.respond("white space can`t be in the given ref name!")
        return
    ComfyHandlersContext().remove_reference(ComfyHandlersManager().get_current_handler().key(), ref)
    await ctx.respond("Remove #{}".format(ref))


@bot.slash_command(name="ref-view", description="View all references")
async def ref_view(ctx):
    respond = "Current references:"
    for key, value in ComfyHandlersContext().get_reference(ComfyHandlersManager().get_current_handler().key()).items():
        respond = "{}\n{} = {}".format(respond, key, value)
    await ctx.respond(respond)


@bot.slash_command(name="prefix", description="Set a prefix for the prompt")
async def set_prefix(ctx, prefix):
    ComfyHandlersContext().set_prefix(ComfyHandlersManager().get_current_handler().key(), prefix)
    await ctx.respond("```Prefix set!```")


@bot.slash_command(name="postfix", description="Set a postfix for the prompt")
async def set_postfix(ctx, postfix):
    ComfyHandlersContext().set_postfix(ComfyHandlersManager().get_current_handler().key(), postfix)
    await ctx.respond("```Postfix set!```")


@bot.slash_command(name="prefix-del", description="Remove the current prompt prefix")
async def remove_prefix(ctx):
    ComfyHandlersContext().remove_prefix(ComfyHandlersManager().get_current_handler().key())
    await ctx.respond("```Prefix removed```")


@bot.slash_command(name="postfix-del", description="Remove the current prompt postfix")
async def remove_postfix(ctx):
    ComfyHandlersContext().remove_postfix(ComfyHandlersManager().get_current_handler().key())
    await ctx.respond("```Postfix removed```")


@bot.slash_command(name="prefix-view", description="View the current prompt prefix")
async def prefix_view(ctx):
    res = ComfyHandlersContext().get_prefix(ComfyHandlersManager().get_current_handler().key())
    if res is None or len(res) == 0:
        res = "```no prefix set!```"
    await ctx.respond(res)


@bot.slash_command(name="postfix-view", description="View the current prompt postfix")
async def postfix_view(ctx):
    res = ComfyHandlersContext().get_postfix(ComfyHandlersManager().get_current_handler().key())
    if res is None or len(res) == 0:
        res = "```no postfix set!```"
    await ctx.respond(res)


@bot.slash_command(name="info", description="information of the current workflow handler")
async def info(ctx):
    prompt_handler = ComfyHandlersManager().get_current_handler()
    await ctx.respond(prompt_handler.info())


@bot.slash_command(name="checkpoints", description="list of all supported checkpoints")
async def checkpoints(ctx: discord.commands.context.ApplicationContext):
    response = "Supported Checkpoints:\n\n"
    for checkpoint in ComfyClient().get_checkpoints():
        response += checkpoint + "\n\n"
    await ctx.respond(response)


async def set_handler(interaction):
    ComfyHandlersManager().set_current_handler(interaction.custom_id)
    await interaction.response.send_message("Handler [{}] selected\n\n{}".format(interaction.custom_id,
                                                                                 ComfyHandlersManager().get_current_handler().info()))


@bot.slash_command(name="handlers", description="list of all handlers")
async def handlers(ctx):
    view = View()
    for handler in ComfyHandlersManager().get_handlers():
        btn = Button(label=handler, style=discord.ButtonStyle.green, custom_id=handler)
        btn.callback = set_handler
        view.add_item(btn)
    await ctx.respond("Select handler:")
    await ctx.send("", view=view)


@bot.slash_command(name="q-status", description="Get queue status")
async def queue_status(ctx):
    queue_data = ComfyClient().get_queue()
    ids = ""
    for data in queue_data['queue_running']:
        ids = "{}\n{}".format(ids, data[1])
    for data in queue_data['queue_pending']:
        ids = "{}\n{}".format(ids, data[1])
    response = "{}\n{}".format(ComfyClient().get_prompt(), ids)
    await ctx.respond(response)


if __name__ == '__main__':
    token = os.getenv('DISCORD_BOT_API_TOKEN')
    os.environ['DISCORD_BOT_API_TOKEN'] = "TOKEN"
    BotDB()
    ComfyHandlersManager()
    ComfyClient()
    bot.run(token)

# class MyView(discord.ui.View):
#     @discord.ui.button(label="Button 1", row=0, style=discord.ButtonStyle.primary)
#     async def first_button_callback(self, button, interaction):
#         await interaction.response.send_message("You pressed me!")
#
#     @discord.ui.button(label="Button 2", row=1, style=discord.ButtonStyle.primary)
#     async def second_button_callback(self, button, interaction):
#         await interaction.response.send_message("You pressed me!")
