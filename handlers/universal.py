import json
import yaml
import re
import random
import datetime
from common import get_logger

class UniversalHandler:
    _neg_token = '!neg!'
    FLAG_REGEX = r'--(\w+)\s+([^\s]+)'

    def __init__(self, yaml_path: str, workflows_dir: str):
        self._logger = get_logger(f"UniversalHandler_{yaml_path}")
        self.yaml_path = yaml_path
        self.workflows_dir = workflows_dir
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        self.key_name = self._config.get('name', 'Unknown')
        self.description_text = self._config.get('description', '')
        self.workflow_filename = self._config.get('workflow_file')
        self.prefix_filename = self._config.get('prefix_filename', 'comfy-bot-')
        self.flag_mappings = self._config.get('flags', {})

        json_path = (self.workflows_dir + "/" + self.workflow_filename).replace("//", "/")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.base_workflow = json.load(f)

    def _convert_value(self, value, data_type):
        if value is None:
            return None
        try:
            if data_type == "integer":
                return int(value)
            elif data_type == "float":
                return float(value)
            elif data_type == "string":
                return str(value)
        except (ValueError, TypeError):
            self._logger.warning(f"Could not convert value '{value}' to type '{data_type}'")
        return value

    def _set_path_value(self, workflow, path, value):
        temp = workflow
        for key in path[:-1]:
            temp = temp.setdefault(key, {})
        temp[path[-1]] = value

    def _get_path_value(self, workflow, path):
        temp = workflow
        for key in path[:-1]:
            if key not in temp:
                return None
            temp = temp[key]
        return temp.get(path[-1])

    def handle(self, message: str) -> dict:
        prompt = json.loads(json.dumps(self.base_workflow)) # Deep copy
        
        # Extract flags
        found_flags = dict(re.findall(self.FLAG_REGEX, message))
        
        # Clean message and handle implicit prompts
        clean_msg = re.sub(self.FLAG_REGEX, '', message).strip()
        parts = clean_msg.split(self._neg_token, maxsplit=1)
        
        positive_val = parts[0] if len(parts) > 0 else ""
        negative_val = parts[1] if len(parts) > 1 else ""

        # Apply flags
        for flag_name, mapping in self.flag_mappings.items():
            val = None
            if mapping.get('is_implicit'):
                if flag_name == 'positive-prompt':
                    val = positive_val
                elif flag_name == 'negative-prompt':
                    val = negative_val
                elif flag_name == 'filesave':
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    val = f"{today}/{self.prefix_filename}"
            else:
                raw_val = found_flags.get(flag_name)
                if raw_val is None:
                    # Use default
                    default_val = mapping.get('default')
                    if default_val == "random":
                        val = random.randint(1, 2**64)
                    else:
                        val = default_val
                else:
                    val = raw_val

            if val is not None:
                data_type = mapping.get('data_type')
                paths = mapping.get('json_path', [])
                splitter = mapping.get('value_splitter')

                if splitter and isinstance(val, str):
                    split_vals = val.split(splitter)
                    for i, path in enumerate(paths):
                        if i < len(split_vals):
                            converted = self._convert_value(split_vals[i], data_type)
                            self._set_path_value(prompt, path, converted)
                else:
                    converted = self._convert_value(val, data_type)
                    for path in paths:
                        self._set_path_value(prompt, path, converted)

        return prompt

    def describe(self, prompt: dict) -> str:
        lines = []
        for flag_name, mapping in self.flag_mappings.items():
            if mapping.get('is_implicit'):
                continue
            paths = mapping.get('json_path', [])
            if not paths:
                continue
            
            # Show first path value or joined if splitter
            val = self._get_path_value(prompt, paths[0])
            if mapping.get('value_splitter') and len(paths) > 1:
                vals = [str(self._get_path_value(prompt, p)) for p in paths]
                val = mapping.get('value_splitter').join(vals)
            
            lines.append(f"{flag_name}: {val}")
        return "\n".join(lines)

    def info(self) -> str:
        info_str = f"# Handler: {self.key_name}\n\n{self.description_text}\n\n## Supported flags:\n\n"
        for flag_name, mapping in self.flag_mappings.items():
            if mapping.get('is_implicit'):
                continue
            desc = mapping.get('description', '')
            default = mapping.get('default', 'None')
            info_str += f"**--{flag_name}**: {desc}, `{default}` default.\n\n"
        
        info_str += f"## Special tokens:\n\n`{self._neg_token}` - will split the message into positive/negative prompts.\n"
        return info_str

    def key(self) -> str:
        return self.key_name

    def default_flags(self) -> str:
        flags = []
        for flag_name, mapping in self.flag_mappings.items():
            if mapping.get('is_implicit'):
                continue
            default = mapping.get('default')
            if default is not None and default != "random":
                flags.append(f"--{flag_name} {default}")
        return "\n".join(flags)
