import re

from comfy_client import get_checkpoints
from comfy_workload import handleGenRequest

text ="a dragon --res 1024:768 running in a forest"

pattern = r'--(\w+)\s+([^\s]+)'
flags = re.findall(pattern, text)

print(flags)

print(re.sub(pattern, '', text).strip())

print(get_checkpoints()["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0])

handleGenRequest(text)