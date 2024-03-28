import os
import random
import io

import discord
from discord import File
from discord.ext import commands
import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
from comfy_client import get_images, CLIENT_ID, SERVER_ADDRESS
from comfy_workloads import prompt_text_ws

# set a sub set intents of what is allowed for the bot from its application config.
intents = discord.Intents.default()
intents.dm_messages = True
bot = commands.Bot(intents=intents, command_prefix="/")

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} bot.')


@bot.event
async def on_message(message):
    # Check if the message is from a user and not the bot itself
    if message.author == bot.user:
        return
    if message.content.startswith("!hello"):
        await message.channel.send("Hi, use !gen to get a picture")
    # Check if the message starts with a specific command or trigger
    if message.content.startswith("!gen"):
        prompt = json.loads(prompt_text_ws)
        # set the text prompt for our positive CLIPTextEncode
        # prompt["6"]["inputs"]["text"] = "a legendary dragon, fantasy, digital painting, action shot, masterpiece, 4k"
        prompt["6"]["inputs"]["text"] = message.content[len("!gen "):]

        # set the seed for our KSampler node
        prompt["3"]["inputs"]["seed"] = random.randint(1, 2**64)
        prompt["3"]["inputs"]["steps"] = 50

        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(SERVER_ADDRESS, CLIENT_ID))

        await message.channel.send("queueing generation, seed: "+str(prompt["3"]["inputs"]["seed"])+" with 50 steps")

        images = get_images(ws, prompt)

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


# Command to get a pong response for slash command 'ping', the guild id is the id of the server that bot in, remove it to update all.
@bot.slash_command(name="ping", guild=discord.Object(id=1111))
async def ping(ctx):
    await ctx.respond("pong")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Create a new bot instance
    bot.run(os.getenv('DISCORD_BOT_API_TOKEN'))
