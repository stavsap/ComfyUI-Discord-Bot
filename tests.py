import re
import importlib
from comfy_client import get_checkpoints
from comfy_handlers_manager import get_current_handler

text ="a dragon --res 1024:768 running in a forest"

pattern = r'--(\w+)\s+([^\s]+)'
flags = re.findall(pattern, text)

print(flags)

print(re.sub(pattern, '', text).strip())

print(get_checkpoints()["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0])

modul_name ="handlers"
class_name = "TxtToImageHandler"

modul = importlib.import_module(modul_name)
dynanic_class= getattr(modul, class_name)

print(dynanic_class().info())

print( getattr(modul, "__all__"))

get_current_handler()
