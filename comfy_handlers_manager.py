import importlib

CURRENT_HANDLER_KEY = "Txt2Img"

HANDLERS = {}


def import_handlers(path=None):
    modul_name = path
    if path is None:
        modul_name = "handlers"
    modul = importlib.import_module(modul_name)
    items = getattr(modul, "__all__")

    for item in items:
        instance = getattr(modul, item)()
        HANDLERS[instance.key()] = instance


def import_all_handlers():
    import_handlers()
    # TODO import custom folder


def get_current_handler():
    return HANDLERS[CURRENT_HANDLER_KEY]


def get_handlers():
    return HANDLERS.keys()


import_all_handlers()
