# ComfyUI Discord Bot - Guidelines for AI Agents

Welcome, AI Agent! This file contains essential instructions, architecture summaries, and guidelines to help you effectively navigate and modify this repository.

## 1. Project Overview

The **ComfyUI Discord Bot** is a bridge layer between Discord users and a ComfyUI backend server. It allows users to run complex generative AI workflows (like text-to-image or image-to-image) natively in Discord using natural language commands, flags, and macros.

### Core Philosophy: Data-Driven Universal Handler Architecture
This project is designed so that **adding new generative capabilities requires NO Python code changes**. Instead, entirely new features are exposed by adding a JSON workflow and a corresponding YAML mapping file to the `workflows/` directory.

## 2. Key Directories & Files

- `workflows/`: The heart of the bot's extensibility. Contains pairs of `.json` (ComfyUI API exported workflows) and `.yaml` (configuration mappings connecting Discord flags to JSON paths).
- `handlers/universal.py`: The `UniversalHandler` engine that parses YAML definitions and dynamically compiles the ComfyUI JSON graph to be sent to the server.
- `comfy_bot.py`: The Discord API interface layer (Pycord) managing slash commands, UI views, and asynchronous queue processing.
- `comfy_client.py`: The ComfyUI client layer connecting to the ComfyUI backend via HTTP (for queuing) and WebSocket (for receiving executing states and retrieving image byte streams).
- `bot_db.py`: SQLite-backed data layer storing macros, dynamic prompt modifiers, and handler contexts.
- `Docs/`: Contains critical architectural documentation (`Design.md`) and instructions on adding new workflows (`universal_handler_guide.md`). **Always consult these docs when unsure.**

## 3. Rules and Guidelines for AI Agents

### 3.1 Adding New Workflows
When a user asks to "add a new workflow" (e.g., txt2img, img2img, upscale):
**DO NOT write a new Python class/handler unless strictly necessary!** Use the Universal Handler system:
1. Place the exported ComfyUI API JSON in the `workflows/` folder (e.g., `workflows/my_workflow.json`).
2. Add the mandatory `SaveImageWebsocket` node to the JSON if it doesn't already exist. It must have the ID `"save_image_websocket_node"` and pipe the images out.
3. Create a corresponding YAML mapping file in `workflows/` (e.g., `workflows/my_workflow.yaml`).
4. Read `Docs/universal_handler_guide.md` to see exactly how to structure the YAML file and map Discord flags (like `--steps`, `--cfg`, and implicit properties like `positive-prompt`) to the correct JSON node paths.

### 3.2 Architectural Changes
- Refer to `Docs/Design.md` for a complete breakdown of how the HTTP/WebSocket execution flow works.
- Keep in mind the asynchronous nature of the `comfy_client.py` and `comfy_bot.py` loops: the bot queues a payload, listens to a WebSocket, captures the image stream into memory, and ships it back asynchronously.

### 3.3 Universal Handler Features
- Recognize that users can configure variables using flags (e.g. `--steps 40`), and you must define how that flag translates to the JSON via `json_path` lists.
- The token `!neg!` is universally used in user messages to split positive and negative prompts.
- Be aware of the `bot_db.py` context system which can automatically apply workflow-specific prefixes or replace macros in user prompts.

### 3.4 General Etiquette
- Before performing deep code tracebacks to understand workflows, always check the `workflows/` directory and `Docs/universal_handler_guide.md` first.
- If modifying dependencies, update `requirements.txt` or the `pyproject.toml`/`uv.lock` as appropriate for the user's setup.

**Final Note**: Always prioritize the Universal Handler approach. This minimizes technical debt and perfectly aligns with the project's data-driven vision.
