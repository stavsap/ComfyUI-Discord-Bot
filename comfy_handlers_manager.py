import importlib
import os

from bot_db import BotDB
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
        self._logger.info("loading module '{}'.".format(modul_name))
        modul = importlib.import_module(modul_name)
        items = getattr(modul, "__all__")

        for item in items:
            instance = getattr(modul, item)()
            self._handlers[instance.key()] = instance
            self._logger.info("handler '{}' added.".format(instance.key()))

    def _import_all_handlers(self):
        self._logger.info("starting import all handlers...")
        self._import_handlers()
        path = "custom_handlers"
        directory_names = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        for name in directory_names:
            self._import_handlers("{}.{}".format(path, name))
        self._logger.info("all handlers imported.")

    def set_current_handler(self, key):
        self._current_handler_key = key
        self._logger.info("current handler set to: {}".format(self._current_handler_key))

    def get_current_handler(self):
        return self._handlers[self._current_handler_key]

    def get_handlers(self):
        return self._handlers.keys()


class ComfyHandlersContext(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self._db: BotDB = BotDB()

    def set_reference(self, handler_key, ref, value):
        self._db.create_or_update_handler_reference(handler_key, "#{}".format(ref), value)

    def remove_reference(self, handler_key, ref):
        self._db.remove_handler_reference(handler_key, "#{}".format(ref))

    def get_reference(self, handler_key):
        res = {}
        refs = self._db.get_all_handler_reference(handler_key)
        for ref in refs:
            res[ref.ref] = ref.value
        return res

    def set_prefix(self, handler_key, prefix):
        self._db.create_or_update_handler_fixes(handler_key,"prefix", prefix)

    def set_postfix(self, handler_key, postfix):
        self._db.create_or_update_handler_fixes(handler_key,"postfix", postfix)

    def remove_prefix(self, handler_key):
        self._db.remove_handler_fixes_by_type(handler_key, "prefix")

    def remove_postfix(self, handler_key):
        self._db.remove_handler_fixes_by_type(handler_key, "postfix")

    def get_prefix(self, handler_key):
        res = None
        for fix in self._db.get_all_handler_fixes(handler_key):
            if fix.type == "prefix":
                res = fix.value
                break
        return res

    def get_postfix(self, handler_key):
        res = None
        for fix in self._db.get_all_handler_fixes(handler_key):
            if fix.type == "postfix":
                res = fix.value
                break
        return res



