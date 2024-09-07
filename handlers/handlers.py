import json
import random
import re
import datetime

from handlers.prompts import TXT_TO_IMAGE_PROMPT, IMG_TO_IMG_PROMPT, INSTANT_ID_BASIC, INSTANT_ID_IP_ADAPTER, \
    IP_ADAPTER_STYLE, FLUX_SCHNELL


def identity(x):
    return [x]


def rev_identity(x):
    return x


def res_spliter(x):
    return x.split(':')


def mapped_value(dict):
    def func(x):
        return [dict[x]]

    return func


def rev_mapped_value(dict):
    def func(x):
        return dict[x]

    return func


class FlagsHandler:

    def __init__(self, regex):
        self._paths_by_flag = {}
        self._funcs_by_flag = {}
        self._descs_by_flag = {}
        self._fetchs_by_flag = {}
        self.FLAG_REGEX = regex

    def set_flags(self, flag_name: str, workflow_paths, description: str = None, convert_func=identity,
                  fetch_func=rev_identity):
        self._paths_by_flag[flag_name] = workflow_paths
        self._funcs_by_flag[flag_name] = convert_func
        self._descs_by_flag[flag_name] = description
        self._fetchs_by_flag[flag_name] = fetch_func

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
            results.append(self._get_value(flag_name, path, prompt))
            index += 1
        return results

    def get_value(self, flag_name: str, prompt):
        for path in self._paths_by_flag[flag_name]:
            return self._get_value(flag_name, path, prompt)
        return None

    def clean_from_flags(self, text):
        return re.sub(self.FLAG_REGEX, '', text).strip()

    def extract_flags(self, text):
        return re.findall(self.FLAG_REGEX, text)

    def _set_value(self, path, prompt, value):
        ref = prompt
        for key in path[:-1]:
            ref = ref[key]
        ref[path[-1]] = value

    def _get_value(self, flag, path, prompt):
        ref = prompt
        for key in path[:-1]:
            ref = ref[key]
        return self._fetchs_by_flag[flag](ref[path[-1]])


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
        self._flags_handler.set_flags("filesave", [["save_image", "inputs", "filename_prefix"]])
        self._flags_handler.set_flags("positive-prompt", [["6", "inputs", "text"]])
        self._flags_handler.set_flags("negative-prompt", [["7", "inputs", "text"]])

    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        parts = positive_prompt.split(self._neg_token, maxsplit=1)

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self._flags_handler.manipulate_prompt("filesave", "{}/{}".format(formatted_date, "comfy-bot-txt-2-img-"), prompt)

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

    def default_flags(self):
        prompt = json.loads(self.workflow_as_text)
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        return f'''
--res {res}
--cfg {cfg}
--steps {steps}
--batch {batch}
--ckpt {checkpoint}
--schd {scheduler}
--sampler {sampler}
'''


class ImgToImageHandler:
    _neg_token = '!neg!'

    def __init__(self):
        self.workflow_as_text = IMG_TO_IMG_PROMPT
        self._flags_handler = FlagsHandler(r'--(\w+)\s+([^\s]+)')
        self._flags_handler.set_flags("steps", [["3", "inputs", "steps"]])
        self._flags_handler.set_flags("seed", [["3", "inputs", "seed"]])
        self._flags_handler.set_flags("cfg", [["3", "inputs", "cfg"]])
        self._flags_handler.set_flags("ckpt", [["4", "inputs", "ckpt_name"]])
        self._flags_handler.set_flags("sampler", [["3", "inputs", "sampler_name"]])
        self._flags_handler.set_flags("schd", [["3", "inputs", "scheduler"]])
        self._flags_handler.set_flags("denoise", [["3", "inputs", "denoise"]])
        self._flags_handler.set_flags("url", [["10", "inputs", "url"]])
        self._flags_handler.set_flags("positive-prompt", [["6", "inputs", "text"]])
        self._flags_handler.set_flags("negative-prompt", [["7", "inputs", "text"]])

        self._flags_handler.set_flags("filesave", [["save_image", "inputs", "filename_prefix"]])


    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        parts = positive_prompt.split(self._neg_token, maxsplit=1)

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self._flags_handler.manipulate_prompt("filesave", "{}/{}".format(formatted_date, "comfy-bot-img-2-img-"), prompt)

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
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))

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
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
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

`{self._neg_token}` - will split the message into positive/negative prompts.
'''

    def key(self):
        return "Img2Img"

    def default_flags(self):
        prompt = json.loads(self.workflow_as_text)
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        return f'''
--cfg {cfg}
--steps {steps}
--denoise {denoise}
--ckpt {checkpoint}
--schd {scheduler}
--sampler {sampler}
--url {url}
'''


class InstantIDFaceHandler:
    _neg_token = '!neg!'

    def __init__(self):
        self.workflow_as_text = INSTANT_ID_BASIC
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
        self._flags_handler.set_flags("denoise", [["3", "inputs", "denoise"]])
        self._flags_handler.set_flags("url", [["67", "inputs", "url"]])

        self._flags_handler.set_flags("instant_id_model", [["11", "inputs", "instantid_file"]])
        self._flags_handler.set_flags("instant_id_provider", [["38", "inputs", "provider"]])

        self._flags_handler.set_flags("instant_id_weight", [["60", "inputs", "weight"]])
        self._flags_handler.set_flags("instant_id_start_at", [["60", "inputs", "start_at"]])
        self._flags_handler.set_flags("instant_id_end_at", [["60", "inputs", "end_at"]])

        self._flags_handler.set_flags("control_net_model", [["16", "inputs", "control_net_name"]])

        self._flags_handler.set_flags("positive-prompt", [["39", "inputs", "text"]])
        self._flags_handler.set_flags("negative-prompt", [["40", "inputs", "text"]])

        self._flags_handler.set_flags("filesave", [["save_image", "inputs", "filename_prefix"]])


    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        parts = positive_prompt.split(self._neg_token, maxsplit=1)

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self._flags_handler.manipulate_prompt("filesave", "{}/{}".format(formatted_date, "comfy-bot-instant-id-basic-"), prompt)

        self._flags_handler.manipulate_prompt("positive-prompt", parts[0], prompt)

        if len(parts) > 1:
            self._flags_handler.manipulate_prompt("negative-prompt", parts[1], prompt)

        self._flags_handler.manipulate_prompt("seed", str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self._flags_handler.manipulate_prompt(flagTuple[0], flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        seed = str(self._flags_handler.get_value("seed", prompt))
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        instant_id_model = str(self._flags_handler.get_value("instant_id_model", prompt))
        instant_id_provider = str(self._flags_handler.get_value("instant_id_provider", prompt))
        instant_id_weight = str(self._flags_handler.get_value("instant_id_weight", prompt))
        instant_id_start_at = str(self._flags_handler.get_value("instant_id_start_at", prompt))
        instant_id_end_at = str(self._flags_handler.get_value("instant_id_end_at", prompt))
        control_net_model = str(self._flags_handler.get_value("control_net_model", prompt))
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
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        instant_id_model = str(self._flags_handler.get_value("instant_id_model", prompt))
        instant_id_provider = str(self._flags_handler.get_value("instant_id_provider", prompt))
        instant_id_weight = str(self._flags_handler.get_value("instant_id_weight", prompt))
        instant_id_start_at = str(self._flags_handler.get_value("instant_id_start_at", prompt))
        instant_id_end_at = str(self._flags_handler.get_value("instant_id_end_at", prompt))
        control_net_model = str(self._flags_handler.get_value("control_net_model", prompt))
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

`{self._neg_token}` - will split the message into positive/negative prompts.
'''

    def key(self):
        return "InstIDFace"

    def default_flags(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        instant_id_model = str(self._flags_handler.get_value("instant_id_model", prompt))
        instant_id_provider = str(self._flags_handler.get_value("instant_id_provider", prompt))
        instant_id_weight = str(self._flags_handler.get_value("instant_id_weight", prompt))
        instant_id_start_at = str(self._flags_handler.get_value("instant_id_start_at", prompt))
        instant_id_end_at = str(self._flags_handler.get_value("instant_id_end_at", prompt))
        control_net_model = str(self._flags_handler.get_value("control_net_model", prompt))
        return f'''
--res {res}
--cfg {cfg}
--batch {batch}
--steps {steps}
--denoise {denoise}
--ckpt {checkpoint}
--schd {scheduler}
--sampler {sampler}
--instant_id_model {instant_id_model}
--instant_id_provider {instant_id_provider}
--instant_id_provider {instant_id_provider}
--instant_id_weight {instant_id_weight}
--instant_id_start_at {instant_id_start_at}
--instant_id_end_at {instant_id_end_at}
--control_net_model {control_net_model}
--url {url}
'''


class InstantIDIpAdapterFaceHandler:
    _neg_token = '!neg!'

    def __init__(self):
        self.workflow_as_text = INSTANT_ID_IP_ADAPTER
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
        self._flags_handler.set_flags("denoise", [["3", "inputs", "denoise"]])
        self._flags_handler.set_flags("url", [["75", "inputs", "url"]])
        self._flags_handler.set_flags("surl", [["76", "inputs", "url"]])

        self._flags_handler.set_flags("instant_id_model", [["11", "inputs", "instantid_file"]])
        self._flags_handler.set_flags("instant_id_provider", [["38", "inputs", "provider"]])

        self._flags_handler.set_flags("instant_id_weight", [["60", "inputs", "weight"]])
        self._flags_handler.set_flags("instant_id_start_at", [["60", "inputs", "start_at"]])
        self._flags_handler.set_flags("instant_id_end_at", [["60", "inputs", "end_at"]])

        self._flags_handler.set_flags("control_net_model", [["16", "inputs", "control_net_name"]])

        self._flags_handler.set_flags("ip_encoder_weight", [["72", "inputs", "weight"]])

        dict = {}
        dict["light"] = "LIGHT - SD1.5 only (low strength)"
        dict["std"] = "STANDARD (medium strength)"
        dict["vit-g"] = "VIT-G (medium strength)"
        dict["plus"] = "PLUS (high strength)"
        dict["plus_face"] = "PLUS FACE (portraits)"
        dict["full_face"] = "FULL FACE - SD1.5 only (portraits stronger)"

        rev_dict = {}

        for key, value in dict.items():
            rev_dict[value] = key

        self._flags_handler.set_flags("ip_unified_preset", [["73", "inputs", "preset"]],
                                      convert_func=mapped_value(dict),
                                      fetch_func=rev_mapped_value(rev_dict))

        self._flags_handler.set_flags("ip_embeds_weight", [["74", "inputs", "weight"]])

        dict = {}

        dict["linear"] = "linear"
        dict["ease_in"] = "ease in"
        dict["ease_out"] = "ease out"
        dict["ease_in-out"] = "ease in-out"
        dict["rev_in-out"] = "reverse in-out"
        dict["weak_input"] = "weak input"
        dict["weak_output"] = "weak output"
        dict["weak_middle"] = "weak middle"
        dict["strong_middle"] = "strong middle"
        dict["style_transfer"] = "style transfer"
        dict["compos"] = "composition"
        dict["strong_style_transfer"] = "strong style transfer"

        rev_dict = {}

        for key, value in dict.items():
            rev_dict[value] = key

        self._flags_handler.set_flags("ip_embeds_weight_type", [["74", "inputs", "weight_type"]],
                                      convert_func=mapped_value(dict),
                                      fetch_func=rev_mapped_value(rev_dict))

        self._flags_handler.set_flags("ip_embeds_start_at", [["74", "inputs", "start_at"]])
        self._flags_handler.set_flags("ip_embeds_end_at", [["74", "inputs", "end_at"]])

        dict = {}
        dict["v"] = "V only"
        dict["k_v"] = "K+V"
        dict["k_v_c_pen"] = "K+V w/ C penalty"
        dict["k_mnv_c_pen"] = "K+mean(V) w/ C penalty"

        for key, value in dict.items():
            rev_dict[value] = key

        self._flags_handler.set_flags("ip_embeds_embeds_scaling", [["74", "inputs", "embeds_scaling"]],
                                      convert_func=mapped_value(dict),
                                      fetch_func=rev_mapped_value(rev_dict))

        self._flags_handler.set_flags("positive-prompt", [["39", "inputs", "text"]])
        self._flags_handler.set_flags("negative-prompt", [["40", "inputs", "text"]])

        self._flags_handler.set_flags("filesave", [["save_image", "inputs", "filename_prefix"]])


    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        parts = positive_prompt.split(self._neg_token, maxsplit=1)

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self._flags_handler.manipulate_prompt("filesave", "{}/{}".format(formatted_date, "comfy-bot-instant-id-ip-adapter-face-"), prompt)

        self._flags_handler.manipulate_prompt("positive-prompt", parts[0], prompt)

        if len(parts) > 1:
            self._flags_handler.manipulate_prompt("negative-prompt", parts[1], prompt)

        self._flags_handler.manipulate_prompt("seed", str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self._flags_handler.manipulate_prompt(flagTuple[0], flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        seed = str(self._flags_handler.get_value("seed", prompt))
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        surl = self._flags_handler.get_value("surl", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        instant_id_model = str(self._flags_handler.get_value("instant_id_model", prompt))
        instant_id_provider = str(self._flags_handler.get_value("instant_id_provider", prompt))
        instant_id_weight = str(self._flags_handler.get_value("instant_id_weight", prompt))
        instant_id_start_at = str(self._flags_handler.get_value("instant_id_start_at", prompt))
        instant_id_end_at = str(self._flags_handler.get_value("instant_id_end_at", prompt))
        control_net_model = str(self._flags_handler.get_value("control_net_model", prompt))

        ip_encoder_weight = str(self._flags_handler.get_value("ip_encoder_weight", prompt))
        ip_unified_preset = str(self._flags_handler.get_value("ip_unified_preset", prompt))

        ip_embeds_weight = str(self._flags_handler.get_value("ip_embeds_weight", prompt))
        ip_embeds_weight_type = str(self._flags_handler.get_value("ip_embeds_weight_type", prompt))
        ip_embeds_start_at = str(self._flags_handler.get_value("ip_embeds_start_at", prompt))
        ip_embeds_end_at = str(self._flags_handler.get_value("ip_embeds_end_at", prompt))
        ip_embeds_embeds_scaling = str(self._flags_handler.get_value("ip_embeds_embeds_scaling", prompt))

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
ip_encoder_weight: {ip_encoder_weight}
ip_unified_preset: {ip_unified_preset}
ip_embeds_weight: {ip_embeds_weight}
ip_embeds_weight_type: {ip_embeds_weight_type}
ip_embeds_start_at: {ip_embeds_start_at}
ip_embeds_end_at: {ip_embeds_end_at}
ip_embeds_embeds_scaling: {ip_embeds_embeds_scaling}
url: {url}
surl: {surl}
'''
        return description

    def info(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        surl = self._flags_handler.get_value("surl", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        instant_id_model = str(self._flags_handler.get_value("instant_id_model", prompt))
        instant_id_provider = str(self._flags_handler.get_value("instant_id_provider", prompt))
        instant_id_weight = str(self._flags_handler.get_value("instant_id_weight", prompt))
        instant_id_start_at = str(self._flags_handler.get_value("instant_id_start_at", prompt))
        instant_id_end_at = str(self._flags_handler.get_value("instant_id_end_at", prompt))
        control_net_model = str(self._flags_handler.get_value("control_net_model", prompt))

        ip_encoder_weight = str(self._flags_handler.get_value("ip_encoder_weight", prompt))
        ip_unified_preset = str(self._flags_handler.get_value("ip_unified_preset", prompt))

        ip_embeds_weight = str(self._flags_handler.get_value("ip_embeds_weight", prompt))
        ip_embeds_weight_type = str(self._flags_handler.get_value("ip_embeds_weight_type", prompt))
        ip_embeds_start_at = str(self._flags_handler.get_value("ip_embeds_start_at", prompt))
        ip_embeds_end_at = str(self._flags_handler.get_value("ip_embeds_end_at", prompt))
        ip_embeds_embeds_scaling = str(self._flags_handler.get_value("ip_embeds_embeds_scaling", prompt))
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

**--surl**: the url to input style image, `{surl}` default.

**--denoise**: the denoise value, `{denoise}` default.

**--instant_id_model**: the ip adapter model, `{instant_id_model}` default.

**--instant_id_provider**: the provider value, `{instant_id_provider}` default.

**--instant_id_weight**: the weight value `[0:1]`, `{instant_id_weight}` default.

**--instant_id_start_at**: the start at value `[0:1]`, `{instant_id_start_at}` default.

**--instant_id_end_at**: the end at value `[0:1]`, `{instant_id_end_at}` default.

**--control_net_model**: the control net model, `{control_net_model}` default.

**--ip_encoder_weight**: the ip encoder weight, `{ip_encoder_weight}` default.

**--ip_unified_preset**: the ip unified preset, `{ip_unified_preset}` default.

**--ip_embeds_weight**: the ip embeds weight `[0:1]`, `{ip_embeds_weight}` default.

**--ip_embeds_weight_type**: the ip embeds weight type, `{ip_embeds_weight_type}` default.

**--ip_embeds_start_at**: the ip embeds start at `[0:1]`, `{ip_embeds_start_at}` default.

**--ip_embeds_end_at**: the ip embeds end at `[0:1]`, `{ip_embeds_end_at}` default.

**--ip_embeds_embeds_scaling**: the ip embeds scaling `supported name`, `{ip_embeds_embeds_scaling}` default.

## Special tokens:

`{self._neg_token}` - will split the message into positive/negative prompts.
'''

    def key(self):
        return "InstIDIpAdapterFace"

    def default_flags(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        surl = self._flags_handler.get_value("surl", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        instant_id_model = str(self._flags_handler.get_value("instant_id_model", prompt))
        instant_id_provider = str(self._flags_handler.get_value("instant_id_provider", prompt))
        instant_id_weight = str(self._flags_handler.get_value("instant_id_weight", prompt))
        instant_id_start_at = str(self._flags_handler.get_value("instant_id_start_at", prompt))
        instant_id_end_at = str(self._flags_handler.get_value("instant_id_end_at", prompt))
        control_net_model = str(self._flags_handler.get_value("control_net_model", prompt))

        ip_encoder_weight = str(self._flags_handler.get_value("ip_encoder_weight", prompt))
        ip_unified_preset = str(self._flags_handler.get_value("ip_unified_preset", prompt))

        ip_embeds_weight = str(self._flags_handler.get_value("ip_embeds_weight", prompt))
        ip_embeds_weight_type = str(self._flags_handler.get_value("ip_embeds_weight_type", prompt))
        ip_embeds_start_at = str(self._flags_handler.get_value("ip_embeds_start_at", prompt))
        ip_embeds_end_at = str(self._flags_handler.get_value("ip_embeds_end_at", prompt))
        ip_embeds_embeds_scaling = str(self._flags_handler.get_value("ip_embeds_embeds_scaling", prompt))

        return f'''
--res {res}
--cfg {cfg}
--batch {batch}
--steps {steps}
--denoise {denoise}
--ckpt {checkpoint}
--schd {scheduler}
--sampler {sampler}
--instant_id_model {instant_id_model}
--instant_id_provider {instant_id_provider}
--instant_id_provider {instant_id_provider}
--instant_id_weight {instant_id_weight}
--instant_id_start_at {instant_id_start_at}
--instant_id_end_at {instant_id_end_at}
--control_net_model {control_net_model}
--ip_encoder_weight {ip_encoder_weight}
--ip_unified_preset {ip_unified_preset}
--ip_embeds_weight {ip_embeds_weight}
--ip_embeds_weight_type {ip_embeds_weight_type}
--ip_embeds_start_at {ip_embeds_start_at}
--ip_embeds_end_at {ip_embeds_end_at}
--ip_embeds_embeds_scaling {ip_embeds_embeds_scaling}
--url {url}
--surl {surl}
'''


class IPAdapterStyleHandler:
    _neg_token = '!neg!'

    def __init__(self):
        self.workflow_as_text = IP_ADAPTER_STYLE
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
        self._flags_handler.set_flags("denoise", [["3", "inputs", "denoise"]])
        self._flags_handler.set_flags("url", [["14", "inputs", "url"]])

        dict = {}
        dict["light"] = "LIGHT - SD1.5 only (low strength)"
        dict["std"] = "STANDARD (medium strength)"
        dict["vit-g"] = "VIT-G (medium strength)"
        dict["plus"] = "PLUS (high strength)"
        dict["plus_face"] = "PLUS FACE (portraits)"
        dict["full_face"] = "FULL FACE - SD1.5 only (portraits stronger)"

        rev_dict = {}

        for key, value in dict.items():
            rev_dict[value] = key

        self._flags_handler.set_flags("ip_unified_preset", [["11", "inputs", "preset"]],
                                      convert_func=mapped_value(dict),
                                      fetch_func=rev_mapped_value(rev_dict))

        self._flags_handler.set_flags("ip_adapter_weight", [["10", "inputs", "weight"]])
        self._flags_handler.set_flags("ip_adapter_start_at", [["10", "inputs", "start_at"]])
        self._flags_handler.set_flags("ip_adapter_end_at", [["10", "inputs", "end_at"]])


        self._flags_handler.set_flags("positive-prompt", [["6", "inputs", "text"]])
        self._flags_handler.set_flags("negative-prompt", [["7", "inputs", "text"]])

        self._flags_handler.set_flags("filesave", [["save_image", "inputs", "filename_prefix"]])


    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        parts = positive_prompt.split(self._neg_token, maxsplit=1)

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self._flags_handler.manipulate_prompt("filesave", "{}/{}".format(formatted_date, "comfy-bot-ip-adapter-style-"), prompt)

        self._flags_handler.manipulate_prompt("positive-prompt", parts[0], prompt)

        if len(parts) > 1:
            self._flags_handler.manipulate_prompt("negative-prompt", parts[1], prompt)

        self._flags_handler.manipulate_prompt("seed", str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self._flags_handler.manipulate_prompt(flagTuple[0], flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        seed = str(self._flags_handler.get_value("seed", prompt))
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        ip_unified_preset = str(self._flags_handler.get_value("ip_unified_preset", prompt))
        ip_adapter_weight = str(self._flags_handler.get_value("ip_adapter_weight", prompt))
        ip_adapter_start_at = str(self._flags_handler.get_value("ip_adapter_start_at", prompt))
        ip_adapter_end_at = str(self._flags_handler.get_value("ip_adapter_end_at", prompt))

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
ip_unified_preset: {ip_unified_preset}
ip_adapter_weight: {ip_adapter_weight}
ip_adapter_start_at: {ip_adapter_start_at}
ip_adapter_end_at: {ip_adapter_end_at}
url: {url}
'''
        return description

    def info(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        ip_adapter_weight = str(self._flags_handler.get_value("ip_adapter_weight", prompt))
        ip_adapter_start_at = str(self._flags_handler.get_value("ip_adapter_start_at", prompt))
        ip_adapter_end_at = str(self._flags_handler.get_value("ip_adapter_end_at", prompt))
        ip_unified_preset = str(self._flags_handler.get_value("ip_unified_preset", prompt))

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

**--ip_unified_preset**: the ip embeds weight `string`, `{ip_unified_preset}` default.

**--ip_adapter_weight**: the ip embeds weight `[0:]`, `{ip_adapter_weight}` default.

**--ip_adapter_start_at**: the ip embeds start at `[0:1]`, `{ip_adapter_start_at}` default.

**--ip_adapter_end_at**: the ip embeds end at `[0:1]`, `{ip_adapter_end_at}` default.

## Special tokens:

`{self._neg_token}` - will split the message into positive/negative prompts.
'''

    def key(self):
        return "IPAdapterStyle"

    def default_flags(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))
        cfg = str(self._flags_handler.get_value("cfg", prompt))
        checkpoint = self._flags_handler.get_value("ckpt", prompt)
        sampler = self._flags_handler.get_value("sampler", prompt)
        scheduler = self._flags_handler.get_value("schd", prompt)
        url = self._flags_handler.get_value("url", prompt)
        denoise = str(self._flags_handler.get_value("denoise", prompt))
        ip_adapter_weight = str(self._flags_handler.get_value("ip_adapter_weight", prompt))
        ip_adapter_start_at = str(self._flags_handler.get_value("ip_adapter_start_at", prompt))
        ip_adapter_end_at = str(self._flags_handler.get_value("ip_adapter_end_at", prompt))
        ip_unified_preset = str(self._flags_handler.get_value("ip_unified_preset", prompt))


        return f'''
--res {res}
--cfg {cfg}
--batch {batch}
--steps {steps}
--denoise {denoise}
--ckpt {checkpoint}
--schd {scheduler}
--sampler {sampler}
--ip_unified_preset {ip_unified_preset}
--ip_adapter_weight {ip_adapter_weight}
--ip_adapter_start_at {ip_adapter_start_at}
--ip_adapter_end_at {ip_adapter_end_at}
--url {url}
'''

class FluxSchnellHandler:

    def __init__(self):
        self.workflow_as_text = FLUX_SCHNELL
        self._flags_handler = FlagsHandler(r'--(\w+)\s+([^\s]+)')
        self._flags_handler.set_flags("res", [["5", "inputs", "height"], ["5", "inputs", "width"]],
                                      convert_func=res_spliter)
        self._flags_handler.set_flags("batch", [["5", "inputs", "batch_size"]])
        self._flags_handler.set_flags("steps", [["17", "inputs", "steps"]])
        self._flags_handler.set_flags("seed", [["25", "inputs", "noise_seed"]])
        self._flags_handler.set_flags("positive-prompt", [["6", "inputs", "text"]])
        self._flags_handler.set_flags("filesave", [["9", "inputs", "filename_prefix"]])


    def handle(self, message):
        prompt = json.loads(self.workflow_as_text)

        flags = self._flags_handler.extract_flags(message)

        positive_prompt = self._flags_handler.clean_from_flags(message)

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self._flags_handler.manipulate_prompt("filesave", "{}/{}".format(formatted_date, "comfy-bot-flux-schnell-"), prompt)

        self._flags_handler.manipulate_prompt("positive-prompt", positive_prompt, prompt)

        self._flags_handler.manipulate_prompt("seed", str(random.randint(1, 2 ** 64)), prompt)

        for flagTuple in flags:
            self._flags_handler.manipulate_prompt(flagTuple[0], flagTuple[1], prompt)
            pass

        return prompt

    def describe(self, prompt):
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        seed = str(self._flags_handler.get_value("seed", prompt))
        steps = str(self._flags_handler.get_value("steps", prompt))

        description = f'''
seed: {seed}
resolution: {res}
steps: {steps}
batch: {batch}
'''
        return description

    def info(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))

        return f'''
# Handler: {self.key()} 

## Supported flags:

**--res**: `height:width`, `{res}` default.

**--steps**: # of steps, `{steps}` default.

**--seed**: seed value, `random` default.

**--batch**: the batch size, `{batch}` default.
'''

    def key(self):
        return "FluxSchnell"

    def default_flags(self):
        prompt = json.loads(self.workflow_as_text)
        batch = str(self._flags_handler.get_value("batch", prompt))
        res = ':'.join([str(num) for num in self._flags_handler.get_values("res", prompt)])
        steps = str(self._flags_handler.get_value("steps", prompt))

        return f'''
--res {res}
--batch {batch}
--steps {steps}
'''
