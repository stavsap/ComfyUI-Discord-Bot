import json
import random
import re

from handlers.prompts import TXT_TO_IMAGE_PROMPT, IMG_TO_IMG_PROMPT, INSTANT_ID_BASIC


def identity(x):
    return [x]


def res_spliter(x):
    return x.split(':')


class FlagsHandler:

    def __init__(self, regex):
        self._paths_by_flag = {}
        self._funcs_by_flag = {}
        self._descs_by_flag = {}
        self.FLAG_REGEX = regex

    def set_flags(self, flag_name: str, workflow_paths, description: str = None, convert_func=identity):
        self._paths_by_flag[flag_name] = workflow_paths
        self._funcs_by_flag[flag_name] = convert_func
        self._descs_by_flag[flag_name] = description

    def get_description(self, flag_name: str) -> str:
        return self._descs_by_flag[flag_name]

    def manipulate_prompt(self, flag_name: str, value: str, prompt):
        results = self._funcs_by_flag[flag_name](value)
        index = 0
        for res in results:
            self._set_value(self._paths_by_flag[flag_name][index], prompt, res)
            index += 1

    def get_values(self, flag_name: str, prompt):
        results = []
        index = 0
        for path in self._paths_by_flag[flag_name]:
            results.append(self._get_value(path, prompt))
            index += 1
        return results

    def get_value(self, flag_name: str, prompt):
        for path in self._paths_by_flag[flag_name]:
            return self._get_value(path, prompt)
        return None

    def _set_value(self, path, prompt, value):
        ref = prompt
        for key in path[:-1]:
            ref = ref[key]
        ref[path[-1]] = value

    def _get_value(self, path, prompt):
        ref = prompt
        for key in path[:-1]:
            ref = ref[key]
        return ref[path[-1]]

    def clean_from_flags(self, text):
        return re.sub(self.FLAG_REGEX, '', text).strip()

    def extract_flags(self, text):
        return re.findall(self.FLAG_REGEX, text)


class TxtToImageHandler:

    _neg_token = '!neg!'
    def __init__(self):
        self.workflow_as_text = TXT_TO_IMAGE_PROMPT
        self._flags_handler = FlagsHandler(r'--(\w+)\s+([^\s]+)')
        self._flags_handler.set_flags("res", [["5", "inputs", "height"], ["5", "inputs", "width"]],
                                      convert_func=res_spliter)
        self._flags_handler.set_flags("batch", [["5", "inputs", "batch_size"]])
        self._flags_handler.set_flags("steps", [["3", "inputs", "steps"]])
        self._flags_handler.set_flags("seed", [["3", "inputs", "seed"]])
        self._flags_handler.set_flags("cfg", [["3", "inputs", "cfg"]])
        self._flags_handler.set_flags("ckpt", [["4", "inputs", "ckpt_name"]])
        self._flags_handler.set_flags("sampler", [["3", "inputs", "sampler_name"]])
        self._flags_handler.set_flags("schd", [["3", "inputs", "scheduler"]])
        self._flags_handler.set_flags("positive-prompt", [["6", "inputs", "text"]])
        self._flags_handler.set_flags("negative-prompt", [["7", "inputs", "text"]])

    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        parts = positive_prompt.split(self._neg_token, maxsplit=1)

        self._flags_handler.manipulate_prompt("positive-prompt", parts[0], prompt)

        if len(parts) > 1:
            self._flags_handler.manipulate_prompt("negative-prompt", parts[1], prompt)

        self._flags_handler.manipulate_prompt("seed", str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self._flags_handler.manipulate_prompt(flagTuple[0], flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        seed = str(self._flags_handler.get_value("seed", prompt))
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)

        description = f'''
checkpoint: {checkpoint}
seed: {seed}
resolution: {res}
steps: {steps}
cfg: {cfg}
batch: {batch}
sampler: {sampler}
scheduler: {scheduler}
'''
        return description

    def info(self):
        prompt = json.loads(self.workflow_as_text)
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        return f'''
# Handler: {self.key()} 

## Supported flags:

**--res**: `height:width`, `{res}` default.

**--cfg**: the CFG value, `{cfg}` default.

**--steps**: # of steps, `{steps}` default.

**--seed**: seed value, `random` default.

**--batch**: the batch size, `{batch}` default.

**--ckpt**: the checkpoint to use, `{checkpoint}` default.

**--schd**: the scheduler to use, `{scheduler}` default.

**--sampler**: the sampler to use, `{sampler}` default.

## Special tokens:

`{self._neg_token}` - will split the message into positive/negative prompts.
'''

    def key(self):
        return "Txt2Img"


class ImgToImageHandler:
    def __init__(self):
        self.flags_funcs = {
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

        parts = positive_prompt.split("!neg!", maxsplit=1)

        prompt["6"]["inputs"]["text"] = parts[0]

        if len(parts) > 1:
            prompt["7"]["inputs"]["text"] = parts[1]

        self._seed(str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self.flags_funcs[flagTuple[0]](flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        seed = str(prompt["3"]["inputs"]["seed"])
        steps = str(prompt["3"]["inputs"]["steps"])
        cfg = str(prompt["3"]["inputs"]["cfg"])
        checkpoint = prompt["4"]["inputs"]["ckpt_name"]
        sampler = prompt["3"]["inputs"]["sampler_name"]
        scheduler = prompt["3"]["inputs"]["scheduler"]
        url = prompt["10"]["inputs"]["url"]
        denoise = str(prompt["3"]["inputs"]["denoise"])

        description = f'''
checkpoint: {checkpoint}
seed: {seed}
steps: {steps}
cfg: {cfg}
sampler: {sampler}
scheduler: {scheduler}
denoise: {denoise}
url: {url}
'''
        return description

    def info(self):
        prompt = json.loads(self.workflow_as_text)
        steps = str(prompt["3"]["inputs"]["steps"])
        cfg = str(prompt["3"]["inputs"]["cfg"])
        checkpoint = prompt["4"]["inputs"]["ckpt_name"]
        sampler = prompt["3"]["inputs"]["sampler_name"]
        scheduler = prompt["3"]["inputs"]["scheduler"]
        url = prompt["10"]["inputs"]["url"]
        denoise = str(prompt["3"]["inputs"]["denoise"])
        return f'''
# Handler: {self.key()} 

## Supported flags:

**--cfg**: the CFG value, `{cfg}` default.

**--steps**: # of steps, `{steps}` default.

**--seed**: seed value, `random` default.

**--ckpt**: the checkpoint to use, `{checkpoint}` default.

**--schd**: the scheduler to use, `{scheduler}` default.

**--sampler**: the sampler to use, `{sampler}` default.

**--url**: the url to input image, `{url}` default.

**--denoise**: the denoise value, `{denoise}` default.

## Special tokens:

`!neg!` - will split the message into positive/negative prompts.
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


class InstantIDFaceHandler:
    def __init__(self):
        self.flags_funcs = {
            'res': self._res,
            'batch': self._batch,
            'steps': self._steps,
            'seed': self._seed,
            'cfg': self._cfg,
            'ckpt': self._ckpt,
            'schd': self._schd,
            'sampler': self._sampler,
            'url': self._url,
            'denoise': self._denoise,

            'instant_id_model': self._instant_id_model,
            'instant_id_provider': self._instant_id_provider,
            'instant_id_weight': self._instant_id_weight,
            'instant_id_start_at': self._instant_id_start_at,
            'instant_id_end_at': self._instant_id_end_at,
            'control_net_model': self._control_net_model,
        }
        self.workflow_as_text = INSTANT_ID_BASIC
        self.FLAG_REGEX = r'--(\w+)\s+([^\s]+)'

    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._extract_flags(message)

        positive_prompt = self._clean_from_flags(message)

        parts = positive_prompt.split("!neg!", maxsplit=1)

        prompt["39"]["inputs"]["text"] = parts[0]

        if len(parts) > 1:
            prompt["40"]["inputs"]["text"] = parts[1]

        self._seed(str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self.flags_funcs[flagTuple[0]](flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        seed = str(prompt["3"]["inputs"]["seed"])
        steps = str(prompt["3"]["inputs"]["steps"])
        cfg = str(prompt["3"]["inputs"]["cfg"])
        checkpoint = prompt["4"]["inputs"]["ckpt_name"]
        batch = str(prompt["5"]["inputs"]["batch_size"])
        res = str(prompt["5"]["inputs"]["height"]) + ":" + str(prompt["5"]["inputs"]["width"])
        sampler = prompt["3"]["inputs"]["sampler_name"]
        scheduler = prompt["3"]["inputs"]["scheduler"]
        url = prompt["67"]["inputs"]["url"]
        denoise = str(prompt["3"]["inputs"]["denoise"])
        instant_id_model = prompt["11"]["inputs"]["instantid_file"]
        instant_id_provider = prompt["38"]["inputs"]["provider"]
        instant_id_weight = prompt["60"]["inputs"]["weight"]
        instant_id_start_at = prompt["60"]["inputs"]["start_at"]
        instant_id_end_at = prompt["60"]["inputs"]["end_at"]
        control_net_model = prompt["16"]["inputs"]["control_net_name"]
        description = f'''
checkpoint: {checkpoint}
seed: {seed}
resolution: {res}
steps: {steps}
cfg: {cfg}
batch: {batch}
sampler: {sampler}
scheduler: {scheduler}
denoise: {denoise}
instant_id_model: {instant_id_model}
instant_id_provider: {instant_id_provider}
instant_id_weight: {instant_id_weight}
instant_id_start_at: {instant_id_start_at}
instant_id_end_at: {instant_id_end_at}
control_net_model: {control_net_model}
url: {url}
'''
        return description

    def info(self):
        prompt = json.loads(self.workflow_as_text)
        steps = str(prompt["3"]["inputs"]["steps"])
        cfg = str(prompt["3"]["inputs"]["cfg"])
        checkpoint = prompt["4"]["inputs"]["ckpt_name"]
        batch = str(prompt["5"]["inputs"]["batch_size"])
        res = str(prompt["5"]["inputs"]["height"]) + ":" + str(prompt["5"]["inputs"]["width"])
        sampler = prompt["3"]["inputs"]["sampler_name"]
        scheduler = prompt["3"]["inputs"]["scheduler"]
        url = prompt["67"]["inputs"]["url"]
        denoise = str(prompt["3"]["inputs"]["denoise"])
        instant_id_model = prompt["11"]["inputs"]["instantid_file"]
        instant_id_provider = prompt["38"]["inputs"]["provider"]
        instant_id_weight = prompt["60"]["inputs"]["weight"]
        instant_id_start_at = prompt["60"]["inputs"]["start_at"]
        instant_id_end_at = prompt["60"]["inputs"]["end_at"]
        control_net_model = prompt["16"]["inputs"]["control_net_name"]
        return f'''
# Handler: {self.key()} 

## Supported flags:

**--res**: `height:width`, `{res}` default.

**--cfg**: the CFG value, `{cfg}` default.

**--steps**: # of steps, `{steps}` default.

**--seed**: seed value, `random` default.

**--batch**: the batch size, `{batch}` default.

**--ckpt**: the checkpoint to use, `{checkpoint}` default.

**--schd**: the scheduler to use, `{scheduler}` default.

**--sampler**: the sampler to use, `{sampler}` default.

**--url**: the url to input image, `{url}` default.

**--denoise**: the denoise value, `{denoise}` default.

**--instant_id_model**: the ip adapter model, `{instant_id_model}` default.

**--instant_id_provider**: the provider value, `{instant_id_provider}` default.

**--instant_id_weight**: the weight value `[0:1]`, `{instant_id_weight}` default.

**--instant_id_start_at**: the start at value `[0:1]`, `{instant_id_start_at}` default.

**--instant_id_end_at**: the end at value `[0:1]`, `{instant_id_end_at}` default.

**--control_net_model**: the control net model, `{control_net_model}` default.

## Special tokens:

`!neg!` - will split the message into positive/negative prompts.
'''

    def key(self):
        return "InstIDFace"

    def _denoise(self, value, workflow):
        workflow["3"]["inputs"]["denoise"] = value

    def _url(self, value, workflow):
        workflow["67"]["inputs"]["url"] = value

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

    def _instant_id_model(self, value, workflow):
        workflow["11"]["inputs"]["instantid_file"] = value

    def _instant_id_provider(self, value, workflow):
        workflow["38"]["inputs"]["provider"] = value

    def _instant_id_weight(self, value, workflow):
        workflow["60"]["inputs"]["weight"] = value

    def _instant_id_start_at(self, value, workflow):
        workflow["60"]["inputs"]["start_at"] = value

    def _instant_id_end_at(self, value, workflow):
        workflow["60"]["inputs"]["end_at"] = value

    def _control_net_model(self, value, workflow):
        workflow["16"]["inputs"]["control_net_name"] = value

    def _clean_from_flags(self, text):
        return re.sub(self.FLAG_REGEX, '', text).strip()

    def _extract_flags(self, text):
        return re.findall(self.FLAG_REGEX, text)
