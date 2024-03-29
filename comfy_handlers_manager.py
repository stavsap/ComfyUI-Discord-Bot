import importlib

from common import get_logger


class ComfyHandlersManager(object):
    _instance = None


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self._logger = get_logger("ComfyHandlersManager")
        self._current_handler_key = "Txt2Img"
        self._handlers = {}
        self._import_all_handlers()

    def _import_handlers(self, path=None):
        modul_name = path
        if path is None:
            modul_name = "handlers"
        modul = importlib.import_module(modul_name)
        items = getattr(modul, "__all__")

        for item in items:
            instance = getattr(modul, item)()
            self._handlers[instance.key()] = instance

    def _import_all_handlers(self):
        self._import_handlers()
        # TODO import custom folder
        self._logger.info("all handlers imported.")

    def set_current_handler(self, key):
        self._current_handler_key = key

    def get_current_handler(self):
        return self._handlers[self._current_handler_key]

    def get_handlers(self):
        return self._handlers.keys()
