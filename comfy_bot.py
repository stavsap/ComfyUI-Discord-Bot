import os
import io
import discord
from discord import File
from discord.ext import commands
import websocket
import uuid

from discord.ui import View, Button

from comfy_client import get_images, CLIENT_ID, SERVER_ADDRESS
from comfy_workload import get_workflow_handler


class MyView(discord.ui.View):
    @discord.ui.button(label="Button 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        await interaction.response.send_message("You pressed me!")

    @discord.ui.button(label="Button 2", row=1, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await interaction.response.send_message("You pressed me!")


intents = discord.Intents.default()
intents.dm_messages = True
bot = commands.Bot(intents=intents, command_prefix="/")


# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} bot.')


async def print_button(interaction):
    print(interaction.custom_id)
    await interaction.response.send_message("You pressed me!")


@bot.event
async def on_message(message):
    # Check if the message is from a user and not the bot itself
    if message.author == bot.user:
        return

    if message.content.startswith("!help"):
        await message.channel.send("Hi, use !gen to get a picture")
    # Check if the message starts with a specific command or trigger
    if message.content.startswith("!gen"):

        prompt_handler = get_workflow_handler()
        prompt = prompt_handler.handle(message.content[len("!gen "):])

        ws = websocket.WebSocket()

        ws.connect("ws://{}/ws?clientId={}".format(SERVER_ADDRESS, CLIENT_ID))

        # await message.channel.send(
        #     "queueing generation, seed: " + str(prompt["3"]["inputs"]["seed"]) + " with 50 steps")

        images = await get_images(ws, prompt, message.channel, prompt_handler)

        for node_id, image_list in images.items():

            # Collect all images from current image list
            imgs = [File(filename=str(uuid.uuid4()) + ".png", fp=io.BytesIO(image_data)) for image_data in image_list]

            for img in imgs:
                await message.channel.send("", file=img)

        await message.channel.send("All complete")
        # # Open the image file
        # with open("example.png", "rb") as f:
        #     picture = discord.File(f)
        #
        # # Send the message with the picture attached
        # await message.channel.send("Here's a picture!", file=picture)

    # experimental
    if message.content == '!button':
        view = View()
        btn = Button(label="Click Me!", style=discord.ButtonStyle.green, custom_id="test_button")
        btn.callback = print_button
        view.add_item(btn)
        await message.channel.send("Here's a buttons!", view=view)


@bot.slash_command(name="ping", guild=discord.Object(id=1111))
async def ping(ctx):
    await ctx.respond("pong")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Create a new bot instance
    bot.run(os.getenv('DISCORD_BOT_API_TOKEN'))
