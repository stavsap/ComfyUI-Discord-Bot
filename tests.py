import re
import importlib
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