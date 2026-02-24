# Universal Workflow Handler Guide

This guide explains how to add and configure new ComfyUI workflows using the **Universal Handler** system. This system allows you to add new bot functionalities by simply creating a JSON workflow file and a corresponding YAML configuration file, without writing any Python code.

---

## 1. File System Structure

All workflows must be placed in the `workflows/` directory at the root of the project:

```text
workflows/
├── txt2img.yaml           # Configuration for the workflow
├── txt2img_workflow.json  # The ComfyUI API JSON (Exported)
├── ggg.yaml               # Another configuration
└── ggg.json               # Another workflow
```

The bot automatically scans this directory on startup and loads any `.yaml` files as new handlers.

---

## 2. JSON Workflow Preparation

1.  **Create your workflow in ComfyUI.**
2.  **Export the API JSON**:
    *   Enable "Dev mode" in ComfyUI settings.
    *   Click "Save (API format)".
3.  **Optimize Node IDs (Optional but Recommended)**:
    *   By default, ComfyUI uses string numbers like `"3"`, `"4"`.
    *   You can rename these to descriptive strings like `"ksampler"`, `"save_image"` for easier mapping in YAML.
4.  **Add Mandatory WebSocket Node**:
    *   To receive images directly in Discord, your workflow **MUST** include a `SaveImageWebsocket` node with the ID `save_image_websocket_node`.
    *   If this node is missing, you must add it manually to your JSON file at the end of the objects list.
    *   **Required Node Snippet**:
        ```json
        "save_image_websocket_node": {
          "class_type": "SaveImageWebsocket",
          "inputs": {
            "images": [
              "8",
              0
            ]
          }
        }
        ```
    *   *Note*: Ensure the input `images` points to the correct node ID that outputs images (e.g., your `VAEDecode` node). In the snippet above, it is connected to node `8`.

---

## 3. YAML Configuration

The YAML file defines how the Discord user interaction maps to the internal nodes of your ComfyUI workflow.

### Basic Metadata
```yaml
name: "MyCustomWorkflow"       # The unique identifier for the handler
description: "Generates stuff" # Shown in /handler-info
workflow_file: "my_wf.json"    # The JSON file in the workflows/ folder
prefix_filename: "my-bot-"     # Prefix for saved files
```

### Flags Configuration
The `flags` section defines the command-line arguments users can pass via `/q`.

#### Standard Flag
```yaml
flags:
  steps:
    description: "Number of sampling steps"
    json_path:
      - ["3", "inputs", "steps"] # Path in the JSON: Node ID -> Section -> Key
    data_type: integer           # integer, float, or string
    default: 20
```

#### Shared/Multi-Path Flag
You can map one flag to multiple nodes in the workflow:
```yaml
  ckpt:
    description: "The model checkpoint"
    json_path:
      - ["4", "inputs", "ckpt_name"]
      - ["10", "inputs", "ckpt_name"] # Updates both nodes
    data_type: string
    default: "v1-5-pruned.safetensors"
```

#### Combined/Split Values
Use `value_splitter` to handle inputs like resolutions (`512x768`):
```yaml
  res:
    description: "Resolution heightxwidth"
    json_path:
      - ["5", "inputs", "height"] # First split part
      - ["5", "inputs", "width"]  # Second split part
    data_type: integer
    value_splitter: "x"
    default: "512x512"
```

### Implicit Flags
Implicit flags are processed automatically from the message content and don't require the `--flag` prefix in Discord.

| Flag Name | Description |
| :--- | :--- |
| `positive-prompt` | The text before the `!neg!` token. |
| `negative-prompt` | The text after the `!neg!` token. |
| `filesave` | Automatically generates a timestamped path for the `SaveImage` node. |

**Example Mapping**:
```yaml
  positive-prompt:
    json_path:
      - ["6", "inputs", "text"]
    data_type: string
    is_implicit: true
```

---

## 4. Special Tokens

*   **`!neg!`**: Used to separate the positive and negative prompt in a single message.
    *   *Usage*: `/q a beautiful cat !neg! low quality, blurry`

---

## 5. Usage in Discord

Once you have added your files:

1.  **Select Handler**: Use `/handlers` and click the button for your new workflow.
2.  **View Information**: Use `/handler-info` to see the description and supported flags.
3.  **Run Prompt**:
    *   Simple: `/q a beautiful landscape`
    *   With Flags: `/q a sunset --res 1024x1024 --steps 30 --cfg 8.5`
    *   With Negative: `/q a forest !neg! people, buildings`

---

## Technical Details: The `json_path`
The `json_path` follows the structure of the ComfyUI API JSON.
If your JSON looks like this:
```json
{
  "12": {
    "inputs": {
      "seed": 12345
    },
    "class_type": "KSampler"
  }
}
```
The YAML path to the seed would be: `["12", "inputs", "seed"]`.
