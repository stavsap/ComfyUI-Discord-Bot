import asyncio
import os
import io
import discord
from discord import File
from discord.ext import commands
import uuid
from discord.ui import View, Button
from dotenv import load_dotenv

from bot_db import BotDB
from comfy_handlers_manager import ComfyHandlersManager, ComfyHandlersContext
from comfy_client import ComfyClient, QueuePromptResult
from common import get_logger

load_dotenv()

intents = discord.Intents.default()
intents.dm_messages = True
bot = commands.Bot(intents=intents, command_prefix="/")
logger = get_logger("ComfyBOT")


def process_message(message):
    # TODO optimize if possible.
    handler_ctx = ComfyHandlersContext()
    current_handler_key = ComfyHandlersManager().get_current_handler().key()
    flags = handler_ctx.get_flags(current_handler_key)
    if flags is not None:
        message = "{} {}".format(flags, message)

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
    logger.debug("processed prompt:\n------------------------\n {}\n------------------------\n".format(message))
    return message


# Event triggered when the bot is ready
@bot.event
async def on_ready():
    if bot.auto_sync_commands:
        logger.debug('sync commands with discord server')
        await bot.sync_commands()
    logger.info(f'on_ready - logged in as {bot.user.name} bot.')


@bot.event
async def on_message(message):
    # Check if the message is from a user and not the bot itself
    if message.author == bot.user:
        return

    if len(message.attachments) > 0:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg', '.m4a']):
                try:
                    # Generate a unique filename
                    filename = f"{message.author.id}_{attachment.filename}"
                    filepath = os.path.join(".", filename)

                    # Download and save the file
                    await attachment.save(filepath)

                    # await message.channel.send(f"✅ Audio file saved: {filename}")

                    play_view = PlayAudioView(filename)
                    await message.channel.send(
                        f"Selected: {filename}",
                        view=play_view
                    )

                except Exception as e:
                    await message.channel.send(f"❌ Failed to save audio file: {str(e)}")
            ans = ""
            if attachment.content_type.startswith('image'):
                ans = "{}\n<{}>".format(ans, attachment.url)
            if len(ans) > 0:
                await message.channel.send(ans)

    if message.content.startswith("help"):
        await message.channel.send("Hi, use '/' commands")


queue_prompt_results: QueuePromptResult = []

class PlayAudioView(discord.ui.View):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    @discord.ui.button(label="Play", style=discord.ButtonStyle.green, emoji="▶️")
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Here you would implement the logic to play the audio
        await interaction.response.send_message(f"Playing {self.filename}...")

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red, emoji="⏹️")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Stopped playback")

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
    # TODO add error handling
    prompt_id = queue_prompt_result.prompt_id
    logger.debug(f"handling prompt result, id:[{prompt_id}]")
    ctx = queue_prompt_result.ctx
    images = queue_prompt_result.images
    prompt_handler = queue_prompt_result.prompt_handler
    try:
        # TODO handle describe more then 2000 chars...
        await ctx.respond(
            "Completed prompt: {}\n{}".format(prompt_id, prompt_handler.describe(queue_prompt_result.prompt)))
        logger.debug(f"handling prompt result, send prompt summary, id:[{prompt_id}]")
        for node_id, image_list in images.items():
            imgs = [File(filename=str(uuid.uuid4()) + ".png", fp=io.BytesIO(image_data)) for image_data in image_list]
            await ctx.respond("", files=imgs)
            logger.debug(f"handling prompt result, sent images, id:[{prompt_id}]")
            # for img in imgs:
            #     await ctx.respond("", files=imgs)
            #     logger.debug(f"handling prompt result, sent image, id:[{prompt_id}]")
    except Exception as e:
        logger.error(f"failed to send results due to: {e}")
        await ctx.respond("error while processing images")


@bot.slash_command(name="q", description="Submit a prompt to current workflow handler")
async def q(ctx: discord.commands.context.ApplicationContext, message):
    await ctx.defer()
    prompt_handler = ComfyHandlersManager().get_current_handler()
    try:
        p = prompt_handler.handle(process_message(message))
    except Exception as e:
        await ctx.respond("```failed to process given message```")
        logger.error(e)
        return
    try:
        ComfyClient().queue_prompt(p, lambda res: handle_queue_prompt_result(ctx, p, prompt_handler, res))
    except Exception as e:
        await ctx.respond("```failed to queue given message```")
        logger.error(e)
        return


@bot.slash_command(name="ref-set", description="Set a reference value")
async def ref_set(ctx, ref, value):
    if '#' in ref:
        await ctx.respond("# can`t be in the given ref name!")
        return
    if ' ' in ref:
        await ctx.respond("white space can`t be in the given ref name!")
        return
    ComfyHandlersContext().set_reference(ComfyHandlersManager().get_current_handler().key(), ref, value)
    await ctx.respond("Set #{}={}".format(ref, value))


@bot.slash_command(name="ref-del", description="Remove a reference")
async def ref_del(ctx, ref):
    if '#' in ref:
        await ctx.respond('# can`t be in the given ref name!')
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


async def set_handler(interaction):
    ComfyHandlersManager().set_current_handler(interaction.custom_id)
    BotDB().create_or_update_global_handler(interaction.custom_id)
    await interaction.response.send_message("Handler [{}] selected\n\n{}".format(interaction.custom_id,
                                                                                 ComfyHandlersManager().get_current_handler().info()))

@bot.slash_command(name="handlers", description="List of all handlers")
async def handlers(ctx):
    view = View()
    for handler in ComfyHandlersManager().get_handlers():
        style = discord.ButtonStyle.gray
        disabled = False
        if handler == ComfyHandlersManager().get_current_handler().key():
            style = discord.ButtonStyle.green
            disabled = True
        btn = Button(label=handler, style=style, custom_id=handler, disabled=disabled)
        btn.callback = set_handler
        view.add_item(btn)
    await ctx.respond("Select handler:")
    await ctx.send("", view=view)


@bot.slash_command(name="handler-info", description="Information about the current workflow handler")
async def handler_info(ctx):
    prompt_handler = ComfyHandlersManager().get_current_handler()
    await ctx.respond(prompt_handler.info())

class HandlerContextModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        handler_ctx = ComfyHandlersContext()
        current_handler_key = ComfyHandlersManager().get_current_handler().key()

        handler_ctx.set_prefix(current_handler_key, self.children[0].value)
        handler_ctx.set_postfix(current_handler_key, self.children[1].value)
        handler_ctx.set_flags(current_handler_key, self.children[2].value)
        await interaction.response.send_message("`all set!`")


@bot.slash_command(name="handler-context", description="Set handler constant context")
async def handler_context(ctx):
    handler_ctx = ComfyHandlersContext()
    current_handler_key = ComfyHandlersManager().get_current_handler().key()
    title = "{} Context".format(current_handler_key[:35])

    modal = HandlerContextModal(title=title)

    flags = handler_ctx.get_flags(current_handler_key)

    if flags is None:
        flags = ComfyHandlersManager().get_current_handler().default_flags()

    modal.add_item(discord.ui.InputText(label="Prefix",
                                        placeholder="Set message prefix, this will be appended in the beginning of the /q {message}",
                                        required=False,
                                        value=handler_ctx.get_prefix(current_handler_key),
                                        style=discord.InputTextStyle.long))
    modal.add_item(discord.ui.InputText(label="Postfix",
                                        placeholder="Set message postfix, this will be appended in the end of the /q {message}",
                                        required=False,
                                        value=handler_ctx.get_postfix(current_handler_key),
                                        style=discord.InputTextStyle.long))
    modal.add_item(discord.ui.InputText(label="Flags",
                                        placeholder="Set constant flags, this will be appended in the beginning of the /q {message}, before the prefix",
                                        required=False,
                                        value= flags,
                                        style=discord.InputTextStyle.long))
    await ctx.send_modal(modal)


@bot.slash_command(name="checkpoints", description="List of all supported checkpoints")
async def checkpoints(ctx: discord.commands.context.ApplicationContext):
    response = "Supported Checkpoints:\n\n"
    for checkpoint in ComfyClient().get_checkpoints():
        response += checkpoint + "\n\n"
    await ctx.respond(response)


@bot.slash_command(name="q-status", description="View queue status")
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
