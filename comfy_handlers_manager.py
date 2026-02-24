import os
from bot_db import BotDB
from common import get_logger
from handlers.universal import UniversalHandler


class ComfyHandlersManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self._logger = get_logger("ComfyHandlersManager")
        self._current_handler_key = BotDB().get_global_handle()
        self._logger.info("Current handler key: '{}'.".format(self._current_handler_key))
        self._handlers = {}
        self._import_all_handlers()

    def _import_universal_handlers(self, workflows_dir="workflows"):
        if not os.path.exists(workflows_dir):
            self._logger.info(f"Workflows directory '{workflows_dir}' not found. Skipping.")
            return

        self._logger.info(f"Scanning for universal handlers in '{workflows_dir}'...")
        for root, dirs, files in os.walk(workflows_dir):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    yaml_path = os.path.join(root, file)
                    try:
                        handler = UniversalHandler(yaml_path, workflows_dir)
                        self._handlers[handler.key()] = handler
                        self._logger.info(f"Universal handler '{handler.key()}' added from {yaml_path}")
                    except Exception as e:
                        self._logger.error(f"Failed to load universal handler from {yaml_path}: {e}")

    def _import_all_handlers(self):
        self._logger.info("Starting import all handlers...")
        
        self._import_universal_handlers()
        
        self._logger.info("All handlers imported.")

    def set_current_handler(self, key):
        self._current_handler_key = key
        self._logger.info("Current handler set to: {}".format(self._current_handler_key))

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
        self._db.create_or_update_handler_fixes(handler_key, "prefix", prefix)

    def set_postfix(self, handler_key, postfix):
        self._db.create_or_update_handler_fixes(handler_key, "postfix", postfix)

    def remove_prefix(self, handler_key):
        self._db.remove_handler_fixes_by_type(handler_key, "prefix")

    def remove_postfix(self, handler_key):
        self._db.remove_handler_fixes_by_type(handler_key, "postfix")

    def set_flags(self, handler_key, flags):
        self._db.create_or_update_handler_fixes(handler_key, "flags", flags)

    def get_flags(self, handler_key):
        res = None
        for fix in self._db.get_all_handler_fixes(handler_key):
            if fix.type == "flags":
                res = fix.value
                break
        return res

    def remove_flags(self, handler_key):
        self._db.remove_handler_fixes_by_type(handler_key, "flags")

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
