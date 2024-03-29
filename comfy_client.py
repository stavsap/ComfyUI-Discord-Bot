import json
from urllib import request, parse
import uuid
import urllib.request
import urllib.parse
import websocket
import os


class ComfyClient(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._comfy_url = os.getenv('COMFY_UI_ADDRESS', '127.0.0.1:8188')
        self._websocket = None
        self._client_id = str(uuid.uuid4())
        self._connect_websocket()

    def _connect_websocket(self):
        self._websocket = websocket.WebSocket()
        self._websocket.connect("ws://{}/ws?clientId={}".format(self._comfy_url, self._client_id))

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self._client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request("http://{}/prompt".format(self._comfy_url), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self._comfy_url, url_values)) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self._comfy_url, prompt_id)) as response:
            return json.loads(response.read())

    def get_checkpoints(self):
        with urllib.request.urlopen("http://{}/object_info/CheckpointLoaderSimple".format(self._comfy_url)) as response:
            return json.loads(response.read())["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]

    async def get_images(self, prompt, channel=None, prompt_handler=None):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        if channel is not None:
            await channel.send("queueing generation! id: " + prompt_id)
        if prompt_handler is not None:
            await channel.send(prompt_handler.describe(prompt))
        output_images = {}
        current_node = ""
        while True:
            out = self._websocket.recv()
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
