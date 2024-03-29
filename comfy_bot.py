import os
import io
import discord
from discord import File
from discord.ext import commands
import uuid

from discord.ui import View, Button

from comfy_handlers_manager import ComfyHandlersManager
from comfy_client import ComfyClient
from common import get_logger

intents = discord.Intents.default()
intents.dm_messages = True
bot = commands.Bot(intents=intents, command_prefix="/")
logger = get_logger("ComfyBOT")

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
            if attachment.content_type.startswith('image'):
                # print(attachment.url)
                pass

    if message.content.startswith("!help"):
        await message.channel.send("Hi, use !gen to get a picture")
    # Check if the message starts with a specific command or trigger
    if message.content.startswith("!gen"):

        prompt_handler = ComfyHandlersManager().get_current_handler()
        p = prompt_handler.handle(message.content[len("!gen "):])

        images = await ComfyClient().get_images(p, message.channel, prompt_handler)

        for node_id, image_list in images.items():

            # Collect all images from current image list
            imgs = [File(filename=str(uuid.uuid4()) + ".png", fp=io.BytesIO(image_data)) for image_data in image_list]

            for img in imgs:
                await message.channel.send("", file=img)

        await message.channel.send("All complete")
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


@bot.slash_command(name="q", description="Submit a prompt to current workflow handler")
async def prompt(ctx, message):
    prompt_handler = ComfyHandlersManager().get_current_handler()
    p = prompt_handler.handle(message)

    await ctx.respond("Prompt received")

    images = await ComfyClient().get_images(p, ctx, prompt_handler)

    for node_id, image_list in images.items():
        imgs = [File(filename=str(uuid.uuid4()) + ".png", fp=io.BytesIO(image_data)) for image_data in image_list]
        for img in imgs:
            await ctx.send("", file=img)

    await ctx.send("All complete")


@bot.slash_command(name="ref-set", description="Set a reference value")
async def ref_set(ctx, ref, value):
    await ctx.respond("Set #{}={}".format(ref, value))


@bot.slash_command(name="ref-del", description="Remove a reference")
async def ref_set(ctx, ref):
    await ctx.respond("Remove #{}".format(ref))


@bot.slash_command(name="info", guild=discord.Object(id=1111),
                   description="information of the current workflow handler")
async def info(ctx):
    prompt_handler = ComfyHandlersManager().get_current_handler()
    await ctx.respond(prompt_handler.info())


@bot.slash_command(name="checkpoints", guild=discord.Object(id=1111), description="list of all supported checkpoints")
async def checkpoints(ctx):
    response = "Supported Checkpoints:\n\n"
    for checkpoint in ComfyClient().get_checkpoints():
        response += checkpoint + "\n\n"
    await ctx.respond(response)


async def set_handler(interaction):
    ComfyHandlersManager().set_current_handler(interaction.custom_id)
    await interaction.response.send_message("Handler [{}] selected\n\n{}".format(interaction.custom_id,
                                                                                 ComfyHandlersManager().get_current_handler().info()))


@bot.slash_command(name="handlers", guild=discord.Object(id=1111), description="list of all handlers")
async def handlers(ctx):
    view = View()
    for handler in ComfyHandlersManager().get_handlers():
        btn = Button(label=handler, style=discord.ButtonStyle.green, custom_id=handler)
        btn.callback = set_handler
        view.add_item(btn)
    await ctx.respond("Select handler:")
    await ctx.send("", view=view)


@bot.slash_command(name="q-status", guild=discord.Object(id=1113), description="Get queue status")
async def queue_status(ctx):
    response = "{}\n{}".format(ComfyClient().get_queue(), ComfyClient().get_prompt())
    await ctx.respond("response")


if __name__ == '__main__':
    token = os.getenv('DISCORD_BOT_API_TOKEN')
    os.environ['DISCORD_BOT_API_TOKEN'] = "TOKEN"
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
