import json
from urllib import request, parse
import uuid
import urllib.request
import urllib.parse
import os
import websocket

address = os.getenv('COMFY_UI_ADDRESS')

SERVER_ADDRESS = "127.0.0.1:8188"

if address is not None:
    SERVER_ADDRESS = address

CLIENT_ID = str(uuid.uuid4())

WEB_SOCKET = websocket.WebSocket()

WEB_SOCKET.connect("ws://{}/ws?clientId={}".format(SERVER_ADDRESS, CLIENT_ID))


def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(SERVER_ADDRESS), data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(SERVER_ADDRESS, url_values)) as response:
        return response.read()


def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(SERVER_ADDRESS, prompt_id)) as response:
        return json.loads(response.read())


def get_checkpoints():
    with urllib.request.urlopen("http://{}/object_info/CheckpointLoaderSimple".format(SERVER_ADDRESS)) as response:
        return json.loads(response.read())


async def get_images(prompt, channel=None, prompt_handler=None):
    prompt_id = queue_prompt(prompt)['prompt_id']
    if channel is not None:
        await channel.send("queueing generation! id: " + prompt_id)
    if prompt_handler is not None:
        await channel.send(prompt_handler.describe(prompt))
    output_images = {}
    current_node = ""
    while True:
        out = WEB_SOCKET.recv()
        # print(out)
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break  # Execution is done
                    else:
                        current_node = data['node']
        else:
            if current_node == 'save_image_websocket_node':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output

    return output_images

# Debug usage.
# Commented out code to display the output images:
# for node_id in images:
#     for image_data in images[node_id]:
#         from PIL import Image
#         import io
#         image = Image.open(io.BytesIO(image_data))
#         image.show()
