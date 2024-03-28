import importlib

CURRENT_HANDLER_KEY = "BASIC"

modul_name = "comfy_workload"

class_name = "WorkflowHandler"

modul = importlib.import_module(modul_name)
basic_workload_handler = getattr(modul, class_name)

instance = basic_workload_handler()

handlers = {instance.key(): instance}


def get_current_workload_handler():
    return handlers[CURRENT_HANDLER_KEY]
