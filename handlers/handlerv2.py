import yaml
import json
import re

REGEX_FLAGS = r'--(\w+)\s+([^\s]+)'

def extract_flags(mapping, text: str):
    extracted_flags = re.findall(REGEX_FLAGS, text)
    result = {}

    for f in extracted_flags:
        result[f[0]] = convert_value(f[1],mapping[f[0]]['data_type'])

    return result

def clean_from_flags(self, text):
    return re.sub(self.FLAG_REGEX, '', text).strip()

def convert_value(value, data_type):
    if value is None:
        return None

    if data_type == "integer":
        return int(value)
    elif data_type == "float":
        return float(value)
    elif data_type == "string":
        return str(value)
    else:
        return value  # Return original if type is not recognized


def get(flag, value, mapping):
    values=[value]
    if 'value_splitter' in mapping[flag]:
        value_splitter = mapping[flag]['value_splitter']
        values = value.split(value_splitter)
    return mapping[flag]['json_path'], values, mapping[flag]['data_type']

def handle_workflow_modification(workflow_json, yaml_path, flags):
    with open(yaml_path, 'r') as f:
        mapping = yaml.safe_load(f)

    modified_workflow = workflow_json.copy()

    for flag, value in flags.items():
        if flag in mapping:
            paths, values, data_type = get(flag, value, mapping)
            index=0
            for path in paths:
                target = modified_workflow
                for key in path[:-1]:
                    target = target.setdefault(key, {})

                try:
                    target[path[-1]] = convert_value(values[index], data_type)
                except ValueError:
                    print(f"Warning: Could not convert value '{values[index]}' for flag '{flag}' to type '{data_type}'.")

    return modified_workflow

# Load the example JSON
comfy_workflow = {
  "17": {
    "inputs": {
      "seed": 42,
      "steps": 20,
      "prompt": "a futuristic cityscape",
      "height": "512",
      "width": "512"
    },
    "class_type": "KSampler"
  },
  "25": {
    "inputs": {
      "filename_prefix": "output",
      "images": [
        "17",
        0
      ]
    },
    "class_type": "SaveImage"
  }
}

# Define the path to the YAML mapping file
yaml_file_path = "mapping_example.yaml"

with open(yaml_file_path, 'r') as f:
    mapping = yaml.safe_load(f)

operational_flags = extract_flags(mapping, "asd asd czx czxvxcvx sadsd --seed 123 --steps 30 --output_prefix modified_output --resolution 1024x768 sdfsdfsdfs")
print(operational_flags)

# Apply the modifications
modified_json = handle_workflow_modification(comfy_workflow, yaml_file_path, operational_flags)

# Print the resulting modified JSON
print(json.dumps(modified_json, indent=2))
