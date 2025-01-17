# ComfyUI Discord Bot

The following is a project for private (can be public) Discord bot integrated with [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

Makes usage of [pycord](https://guide.pycord.dev/installation), also check [pycord github](https://github.com/Pycord-Development/pycord/)

For quick installation of ComfyUI with all the required models [check this](https://github.com/stavsap/ComfyUI-Playground).

## 🚦 WIP 🚦

<a href="https://www.buymeacoffee.com/stavsapq" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="30" width="150"></a>

![pic](.meta/prompt.png)

![pic](.meta/screenshot.png)

## Setup

Install dependencies:

```shell
python -m pip install -r requirements.txt
```

## Bot Setup

For Bot creation and integration check the [docs](Docs/BotSetup.md)

To run the bot after creating and obtaining the bot Token, set environment variables:


| Env Var | Description                                     | Default        | Required? |
|---------|-------------------------------------------------|----------------|-----------|
| DISCORD_BOT_API_TOKEN  | A token to access Discord API                   |                | YES     |
| COMFY_UI_HOST | The host address of comfy ui server `host:port` | 127.0.0.1:8188 | NO      |
| COMFY_BOT_LOG_LEVEL | The log level.                                  | INFO           | NO      |

# Docker

To build a docker image:

```shell
docker build -t comfy-discord-bot:1 .
```

the database will be in the following path in the container:

`/bot/db`

# Contribution

If you want to contribute, feel free to fork the repository and submit a Pull Request. When creating the PR, please provide a high-level description of the changes or new feature being merged.