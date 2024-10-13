import json
from concurrent.futures import ThreadPoolExecutor
from urllib import request, parse
import uuid
import urllib.request
import urllib.parse
import websocket
import os

from common import get_logger


class QueuePromptResult:
    def __init__(self, prompt_id: str, status: bool, images, ctx=None, prompt=None, prompt_handler=None):
        self.ctx = ctx
        self.prompt_id = prompt_id
        self.prompt = prompt
        self.status = status
        self.images = images
        self.prompt_handler = prompt_handler


# TODO add TLS support + insecure flag + trust cert option. TLS + wss.

class ComfyClient(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self._protocol = "http"
        self._socket_protocol = "ws"
        self._logger = get_logger("ComfyClient")
        self._comfy_url = os.getenv('COMFY_UI_HOST', '127.0.0.1:8188')
        self._websocket = None
        self._client_id = str(uuid.uuid4())
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._executor.submit(self._connect_websocket)
        self._callbacks = []
        self._prompt_ids = []
        self._logger.info(
            "comfy client created with client id [{}] and comfy server at [{}].".format(self._client_id, self._comfy_url))

    def _connect_websocket(self):
        self._websocket = websocket.WebSocket()
        self._websocket.connect(
            "{}://{}/ws?clientId={}".format(self._socket_protocol, self._comfy_url, self._client_id))
        output_images = {}
        current_node = ""
        while True:
            out = self._websocket.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if len(self._prompt_ids) > 0 and data['prompt_id'] == self._prompt_ids[0]:
                        if data['node'] is None:
                            self._callbacks[0](
                                QueuePromptResult(prompt_id=self._prompt_ids[0], images=output_images, status=True))
                            self._prompt_ids = self._prompt_ids[1:]
                            self._callbacks = self._callbacks[1:]
                            output_images = {}
                            current_node = ""
                            pass
                        else:
                            current_node = data['node']
            else:
                if current_node == 'save_image_websocket_node':
                    images_output = output_images.get(current_node, [])
                    images_output.append(out[8:])
                    output_images[current_node] = images_output

    def queue_prompt(self, prompt, callback):
        p = {"prompt": prompt, "client_id": self._client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request("{}://{}/prompt".format(self._protocol, self._comfy_url), data=data)
        self._callbacks.append(callback)
        prompt_id = json.loads(urllib.request.urlopen(req).read())['prompt_id']
        self._prompt_ids.append(prompt_id)
        return prompt_id

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("{}://{}/view?{}".format(self._protocol, self._comfy_url, url_values)) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen(
                "{}://{}/history/{}".format(self._protocol, self._comfy_url, prompt_id)) as response:
            return json.loads(response.read())

    def get_checkpoints(self):
        with urllib.request.urlopen(
                "{}://{}/object_info/CheckpointLoaderSimple".format(self._protocol, self._comfy_url)) as response:
            return json.loads(response.read())["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]

    def get_system_stats(self):
        with urllib.request.urlopen("{}://{}/system_stats".format(self._protocol, self._comfy_url)) as response:
            return json.loads(response.read())

    def get_prompt(self):
        with urllib.request.urlopen("{}://{}/prompt".format(self._protocol, self._comfy_url)) as response:
            return json.loads(response.read())

    def get_queue(self):
        with urllib.request.urlopen("{}://{}/queue".format(self._protocol, self._comfy_url)) as response:
            return json.loads(response.read())

    def get_history(self):
        with urllib.request.urlopen("{}://{}/history".format(self._protocol, self._comfy_url)) as response:
            return json.loads(response.read())

    def get_history_by_prompt_id(self, prompt_id):
        with urllib.request.urlopen(
                "{}://{}/history/{}".format(self._protocol, self._comfy_url, prompt_id)) as response:
            return json.loads(response.read())

    def get_embeddings(self):
        with urllib.request.urlopen("{}://{}/embeddings".format(self._protocol, self._comfy_url)) as response:
            return json.loads(response.read())

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
