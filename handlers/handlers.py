import json
import random
import re

from handlers.prompts import TXT_TO_IMAGE_PROMPT, IMG_TO_IMG_PROMPT


class TxtToImageHandler:
    def __init__(self):
        self.flags_dic = {
            'res': self._res,
            'batch': self._batch,
            'steps': self._steps,
            'seed': self._seed,
            'cfg': self._cfg,
            'ckpt': self._ckpt,
            'schd': self._schd,
            'sampler': self._sampler,
        }
        self.workflow_as_text = TXT_TO_IMAGE_PROMPT
        self.FLAG_REGEX = r'--(\w+)\s+([^\s]+)'

    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._extract_flags(message)

        positive_prompt = self._clean_from_flags(message)

        # set the text prompt for our positive CLIPTextEncode
        # prompt["6"]["inputs"]["text"] = "a legendary dragon, fantasy, digital painting, action shot, masterpiece, 4k"
        prompt["6"]["inputs"]["text"] = positive_prompt

        self._res("768:768", prompt)
        self._batch("1", prompt)
        self._steps("25", prompt)
        self._cfg("7", prompt)
        self._seed(str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self.flags_dic[flagTuple[0]](flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        seed = prompt["3"]["inputs"]["seed"]
        steps = prompt["3"]["inputs"]["steps"]
        cfg = prompt["3"]["inputs"]["cfg"]
        checkpoint = prompt["4"]["inputs"]["ckpt_name"]
        batch = prompt["5"]["inputs"]["batch_size"]
        res = prompt["5"]["inputs"]["height"] + ":" + prompt["5"]["inputs"]["width"]

        description = f'''
checkpoint: {checkpoint}
cfg: {cfg}
steps: {steps}
seed: {seed}
batch: {batch}
resolution: {res}
'''
        return description

    def info(self):
        return f'''
workflow: {self.key()} 

supported flags:

--res: Y:X, where Y is height and X is width. 768:768 if not present.

--cfg: the CFG value, 7 if not present.

--steps: # of steps, 25 if not present.

--seed: seed value, random if not present.

--batch: the batch size, 1 if not present.

--ckpt: the checkpoint to use, sdxl\\\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors if not present.

--schd: the scheduler to use, normal if not present.

--sampler: the sampler to use, euler if not present.
'''

    def key(self):
        return "Txt2Img"

    def _res(self, value, workflow):
        split = value.split(':')
        workflow["5"]["inputs"]["height"] = split[0]
        workflow["5"]["inputs"]["width"] = split[1]

    def _batch(self, value, workflow):
        workflow["5"]["inputs"]["batch_size"] = value

    def _steps(self, value, workflow):
        workflow["3"]["inputs"]["steps"] = value

    def _seed(self, value, workflow):
        workflow["3"]["inputs"]["seed"] = value

    def _cfg(self, value, workflow):
        workflow["3"]["inputs"]["cfg"] = value

    def _ckpt(self, value, workflow):
        workflow["4"]["inputs"]["ckpt_name"] = value

    def _sampler(self, value, workflow):
        workflow["3"]["inputs"]["sampler_name"] = value

    def _schd(self, value, workflow):
        workflow["3"]["inputs"]["scheduler"] = value

    def _clean_from_flags(self, text):
        return re.sub(self.FLAG_REGEX, '', text).strip()

    def _extract_flags(self, text):
        return re.findall(self.FLAG_REGEX, text)


class ImgToImageHandler:
    def __init__(self):
        self.flags_dic = {
            'steps': self._steps,
            'seed': self._seed,
            'cfg': self._cfg,
            'ckpt': self._ckpt,
            'schd': self._schd,
            'sampler': self._sampler,
            'url': self._url,
            'denoise': self._denoise,
        }
        self.workflow_as_text = IMG_TO_IMG_PROMPT
        self.FLAG_REGEX = r'--(\w+)\s+([^\s]+)'

    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._extract_flags(message)

        positive_prompt = self._clean_from_flags(message)

        # set the text prompt for our positive CLIPTextEncode
        # prompt["6"]["inputs"]["text"] = "a legendary dragon, fantasy, digital painting, action shot, masterpiece, 4k"
        prompt["6"]["inputs"]["text"] = positive_prompt

        self._steps("25", prompt)
        self._cfg("7", prompt)
        self._seed(str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self.flags_dic[flagTuple[0]](flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        seed = prompt["3"]["inputs"]["seed"]
        steps = prompt["3"]["inputs"]["steps"]
        cfg = prompt["3"]["inputs"]["cfg"]
        checkpoint = prompt["4"]["inputs"]["ckpt_name"]

        description = f'''
checkpoint: {checkpoint}
cfg: {cfg}
steps: {steps}
seed: {seed}
'''
        return description

    def info(self):
        return f'''
workflow: {self.key()} 

supported flags:

--url: url to the source image.

--denoise: set denoise level with generation and source image. near 0 is more source image, more to 1 is generation.

--cfg: the CFG value, 7 if not present.

--steps: # of steps, 25 if not present.

--seed: seed value, random if not present.

--ckpt: the checkpoint to use, sdxl\\\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors if not present.

--schd: the scheduler to use, normal if not present.

--sampler: the sampler to use, euler if not present.
'''

    def key(self):
        return "Img2Img"

    def _denoise(self, value, workflow):
        workflow["3"]["inputs"]["denoise"] = value

    def _url(self, value, workflow):
        workflow["10"]["inputs"]["url"] = value

    def _steps(self, value, workflow):
        workflow["3"]["inputs"]["steps"] = value

    def _seed(self, value, workflow):
        workflow["3"]["inputs"]["seed"] = value

    def _cfg(self, value, workflow):
        workflow["3"]["inputs"]["cfg"] = value

    def _ckpt(self, value, workflow):
        workflow["4"]["inputs"]["ckpt_name"] = value

    def _sampler(self, value, workflow):
        workflow["3"]["inputs"]["sampler_name"] = value

    def _schd(self, value, workflow):
        workflow["3"]["inputs"]["scheduler"] = value

    def _clean_from_flags(self, text):
        return re.sub(self.FLAG_REGEX, '', text).strip()

    def _extract_flags(self, text):
        return re.findall(self.FLAG_REGEX, text)
