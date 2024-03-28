FROM python:3.10.13-alpine3.19
WORKDIR /bot
COPY . .
RUN pip install -r requirements.txt
ENV DISCORD_BOT_API_TOKEN=SET_ME_EXTERNALY
ENV COMFY_UI_ADDRESS=127.0.0.1:8188
CMD ["python","comfy_bot.py"]