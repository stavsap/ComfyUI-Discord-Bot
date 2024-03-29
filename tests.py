import re
import importlib

from comfy_client import ComfyClient
from comfy_handlers_manager import ComfyHandlersManager
from handlers import ImgToImageHandler

text ="a dragon --res 1024:768 running in a forest"

pattern = r'--(\w+)\s+([^\s]+)'
flags = re.findall(pattern, text)

print(flags)

print(re.sub(pattern, '', text).strip())

modul_name ="handlers"
class_name = "TxtToImageHandler"

modul = importlib.import_module(modul_name)
dynanic_class= getattr(modul, class_name)

print(dynanic_class().info())

print( getattr(modul, "__all__"))

ComfyHandlersManager()

ImgToImageHandler().handle("xzczxczxc")

print(ComfyClient().get_embeddings())

text ="sadkasdka #moo sdfsdfsdf #mbcvbc"

hashtag_pattern = r'#\w+'

# Find all matches of the pattern in the text
hashtags = re.findall(hashtag_pattern, text)

print(hashtags)