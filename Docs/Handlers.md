# Workflow Handlers

TODO description


# Built In Handlers

1. [Txt 2 Image](#text-2-image)
2. [Image 2 Image](#image-2-image)
3. [InstantID Face](#instantid-face)
4. [InstantID + IP Adapter Face](#instantid-face--ip-adapter-)
4. [IPAdapter Style](#ip-adapter-style-)
4. [Flux Schnell](#flux-schnell)

## Text 2 Image

Simple basic workflow that does not require any additional custom nodes.

#### Supported Flags:

Flags can be added to the message to control specific parameters in the prompts that will be passed to comfy. The flags and their values will be omitted from the final prompts.

| Flag      | Description                                                     | Default                                                |
|-----------|-----------------------------------------------------------------|--------------------------------------------------------|
| --res     | resolution in format of `height:width`                          | 768:768                                                |
| --steps   | amount of steps `[1:]`                                       | 25                                                     |
| --seed    | seed value `int`                                                | random                                                 |
| --cfg     | CFG value `int`                                                 | 7                                                      |
| --batch   | the amount of images to generate `[1:]`                      | 1                                                      |
| --ckpt    | the path to the checkpoint in comfy `models/checkpoint` folder. | sdxl\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors |
| --sampler | the sampler to use `supported name`                             | euler                                                  |
| --schd    | the scheduler to use `supported name`                           | normal                                                 |

#### Special tokens

| Token | Description                                                                                                                                                                                          |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| !neg! | if this token present in the message it will split the message into 2 parts. first part will be positive prompt, the second one negative. if not present message is considered positive prompt only. | 



## Image 2 Image

Basic image to image workflow.

Image is given as a url via --url flag.

Requires: https://github.com/glowcone/comfyui-load-image-from-url custom node to be able to load images from urls.

**Note**: the resolution is set by the input image!

#### Supported Flags:

Flags can be added to the message to control specific parameters in the prompts that will be passed to comfy. The flags and their values will be omitted from the final prompts.

| Flag      | Description                                                     | Default                                                                           |
|-----------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------|
| --steps   | amount of steps `[1:]`                                          | 20                                                                                |
| --seed    | seed value `int`                                                | random                                                                            |
| --cfg     | CFG value `int`                                                 | 8                                                                                 |
| --ckpt    | the path to the checkpoint in comfy `models/checkpoint` folder. | sdxl\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors                            |
| --sampler | the sampler to use `supported name`                             | dpmpp_2m                                                                          |
| --schd    | the scheduler to use `supported name`                           | normal                                                                            |
| --url     | the url to source image `valid url`                             | https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/input/example.png |
| --denoise | the denoise to use `[0:1]`                                      | 0.87                                                                              |

#### Special tokens

| Token | Description                                                                                                                                                                                          |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| !neg! | if this token present in the message it will split the message into 2 parts. first part will be positive prompt, the second one negative. if not present message is considered positive prompt only. | 


## InstantID Face

InstantID workflow. Thanks to **matt3o**! https://github.com/cubiq/ComfyUI_InstantID.

Source image is given as a url via --url flag.

Requires: 

- https://github.com/glowcone/comfyui-load-image-from-url custom node to be able to load images from urls.
- https://github.com/cubiq/ComfyUI_InstantID - Instant ID nodes.

#### Supported Flags:

Flags can be added to the message to control specific parameters in the prompts that will be passed to comfy. The flags and their values will be omitted from the final prompts.

| Flag                  | Description                                                     | Default                                                                                                              |
|-----------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| --res                 | resolution in format of `height:width`                          | 1024:1024                                                                                                            |
| --batch               | the amount of images to generate `[1:]`                         | 1                                                                                                                    |
| --steps               | amount of steps `[1:]`                                          | 30                                                                                                                   |
| --seed                | seed value `int`                                                | random                                                                                                               |
| --cfg                 | CFG value `int`                                                 | 4.5                                                                                                                   |
| --ckpt                | the path to the checkpoint in comfy `models/checkpoint` folder. | sdxl\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors                                                               |
| --sampler             | the sampler to use `supported name`                             | ddpm                                                                                                             |
| --schd                | the scheduler to use `supported name`                           | karras                                                                                                               |
| --url                 | the url to source image `valid url`                             | https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/19b050360d36e076c33460dd327587561d23adcc/.meta/man.png |
| --denoise             | the denoise to use `[0:1]`                                      | 1                                                                                                                    |
| --instant_id_model    | the model from `models/instantid`                               | ip-adapter.bin                                                                                                       |
| --instant_id_provider | the provider `CPU \| CUDA \| ROCM`                              | CPU                                                                                                                  |
| --instant_id_weight   | the weight to use `[0:1]`                                       | 0.8                                                                                                                  |
| --instant_id_start_at | the start at to use `[0:1]`                                     | 0                                                                                                                    |
| --instant_id_end_at   | the end at to use `[0:1]`                                       | 1                                                                                                                    |
| --control_net_model   | the control net model from `models/controlnet`                  | diffusion_pytorch_model.safetensors                                                                                  |
#### Special tokens

| Token | Description                                                                                                                                                                                          |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| !neg! | if this token present in the message it will split the message into 2 parts. first part will be positive prompt, the second one negative. if not present message is considered positive prompt only. | 

## InstantID Face + IP Adapter 

InstantID combined with IP Adapter workflow. Thanks to **matt3o**! [InstantID](https://github.com/cubiq/ComfyUI_InstantID) and [IP Adapter](https://github.com/cubiq/ComfyUI_IPAdapter_plus).

Create given face and style image a generation of the face combined with style.

Source image is given as a url via `--url` flag.

Style image is given as a surl via `--surl` flag.

#### Requires: 

- https://github.com/glowcone/comfyui-load-image-from-url custom node to be able to load images from urls.
- https://github.com/cubiq/ComfyUI_InstantID - Instant ID nodes.
- https://github.com/cubiq/ComfyUI_IPAdapter_plus - IP Adapters nodes.

#### Supported Flags:

Flags can be added to the message to control specific parameters in the prompts that will be passed to comfy. The flags and their values will be omitted from the final prompts.

| Flag                    | Description                                                     | Default                                                                                                              |
|-------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| --res                   | resolution in format of `height:width`                          | 1024:1024                                                                                                            |
| --batch                 | the amount of images to generate `[1:]`                         | 1                                                                                                                    |
| --steps                 | amount of steps `[1:]`                                          | 30                                                                                                                   |
| --seed                  | seed value `int`                                                | random                                                                                                               |
| --cfg                   | CFG value `int`                                                 | 4.5                                                                                                                  |
| --ckpt                  | the path to the checkpoint in comfy `models/checkpoint` folder. | sdxl\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors                                                               |
| --sampler               | the sampler to use `supported name`                             | ddpm                                                                                                                 |
| --schd                  | the scheduler to use `supported name`                           | karras                                                                                                               |
| --url                   | the url to source image `valid url`                             | https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/19b050360d36e076c33460dd327587561d23adcc/.meta/man.png |
| --surl                  | the url to source style image `valid url`                       | https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/main/.meta/king.jpg                                    |
| --denoise               | the denoise to use `[0:1]`                                      | 1                                                                                                                    |
| --instant_id_model      | the model from `models/instantid`                               | ip-adapter.bin                                                                                                       |
| --instant_id_provider   | the provider `CPU \| CUDA \| ROCM`                              | CPU                                                                                                                  |
| --instant_id_weight     | the weight to use `[0:1]`                                       | 0.8                                                                                                                  |
| --instant_id_start_at   | the start at to use `[0:1]`                                     | 0                                                                                                                    |
| --instant_id_end_at     | the end at to use `[0:1]`                                       | 1                                                                                                                    |
| --control_net_model     | the control net model from `models/controlnet`                  | diffusion_pytorch_model.safetensors                                                                                  |
| --ip_encoder_weight     | the ip encoder weight                                           | 1                                                                                                                    |
| --ip_unified_preset     | the ip unified preset                                           | plus                                                                                                                 |
| --ip_embeds_weight      | the ip embeds weight `[0:1]`                                    | 0.8                                                                                                                  |
| --ip_embeds_weight_type | the ip embeds weight type `supported names`                     | linear                                                                                                               |
| --ip_embeds_start_at    | the ip embeds start at `[0:1]`                                  | 0                                                                                                                    |
| --ip_embeds_end_at      | the ip embeds end at `[0:1]`                                    | 1                                                                                                                    |
| --ip_embeds_embeds_scaling      | the ip embeds scaling `supported names`                         | v                                                                                                                    |

#### Special tokens

| Token | Description                                                                                                                                                                                          |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| !neg! | if this token present in the message it will split the message into 2 parts. first part will be positive prompt, the second one negative. if not present message is considered positive prompt only. | 

## IP Adapter Style 

IPAdapter style on a given url image. Thanks to **matt3o**! [IP Adapter](https://github.com/cubiq/ComfyUI_IPAdapter_plus).

Source image is given as a url via `--url` flag.

#### Requires: 

- https://github.com/glowcone/comfyui-load-image-from-url custom node to be able to load images from urls.
- https://github.com/cubiq/ComfyUI_IPAdapter_plus - IP Adapters nodes.

#### Supported Flags:

Flags can be added to the message to control specific parameters in the prompts that will be passed to comfy. The flags and their values will be omitted from the final prompts.

| Flag                 | Description                                                    | Default                                                                           |
|----------------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------|
| --res                | resolution in format of `height:width`                         | 768:768                                                                         |
| --batch              | the amount of images to generate `[1:]`                        | 1                                                                                 |
| --steps              | amount of steps `[1:]`                                         | 20                                                                                |
| --seed               | seed value `int`                                               | random                                                                            |
| --cfg                | CFG value `int`                                                | 8                                                                                 |
| --ckpt               | the path to the checkpoint in comfy `models/checkpoint` folder. | sdxl\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors                            |
| --sampler            | the sampler to use `supported name`                            | euler                                                                             |
| --schd               | the scheduler to use `supported name`                          | normal                                                                            |
| --url                | the url to source image `valid url`                            | https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/main/.meta/king.jpg |
| --denoise            | the denoise to use `[0:1]`                                     | 1                                                                                 |
| --ip_unified_preset     | the ip unified preset                                           | plus                                                                                                 |
| --ip_adapter_weight  | the ip embeds weight `[0:]`                                    | 1                                                                                 |
| --ip_adapter_start_at | the ip embeds start at `[0:1]`                                 | 0                                                                                 |
| --ip_adapter_end_at   | the ip embeds end at `[0:1]`                                   | 1                                                                                 |

#### Special tokens

| Token | Description                                                                                                                                                                                          |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| !neg! | if this token present in the message it will split the message into 2 parts. first part will be positive prompt, the second one negative. if not present message is considered positive prompt only. | 

## Flux Schnell

Basic Flux Schnell workflow.

#### Requires: 

- Flux Models, Clips and Vae.
- 
#### Supported Flags:

Flags can be added to the message to control specific parameters in the prompts that will be passed to comfy. The flags and their values will be omitted from the final prompts.

| Flag                 | Description                                                    | Default   |
|----------------------|----------------------------------------------------------------|-----------|
| --res                | resolution in format of `height:width`                         | 1024:1024 |
| --batch              | the amount of images to generate `[1:]`                        | 1         |
| --steps              | amount of steps `[1:]`                                         | 4         |
| --seed               | seed value `int`                                               | random    |


# Custom Handlers

The bot supports in loading dynamically handlers from the `custom_handlers` folder. just put your handlers module in similar way to the built-in [handlers](../handlers/) module.

If your module is a git repo, just git clone into the `custom_handlers` folder and reboot the bot.


## Nodes required for integration

The following nodes are a must for workflow that is handled by a handler.

### SaveImageWebsocket

This node should input the final images of the workflow, sending images to this node will result in images to be published by the bot back to the user.

![pic](../.meta/save-to-socket-node.png)

```json
{
  "save_image_websocket_node": {
    "inputs": {
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImageWebsocket",
    "_meta": {
      "title": "SaveImageWebsocket"
    }
  }
}
```
