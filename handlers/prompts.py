
TXT_TO_IMAGE_PROMPT = """
{
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 7,
            "denoise": 1,
            "latent_image": [
                "5",
                0
            ],
            "model": [
                "4",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 123456789,
            "steps": 25
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "sdxl\\\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 1,
            "height": 768,
            "width": 768
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": ""
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": ""
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
        }
    },
    "save_image_websocket_node": {
        "class_type": "SaveImageWebsocket",
        "inputs": {
            "images": [
                "8",
                0
            ]
        }
    },
    "save_image": {
    "inputs": {
      "filename_prefix": "comfy-bot-txt-2-img-",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""

IMG_TO_IMG_PROMPT = """
{
  "3": {
    "inputs": {
      "seed": 333592799566352,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "dpmpp_2m",
      "scheduler": "normal",
      "denoise": 0.87,
      "model": [
        "4",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "11",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "sdxl\\\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "6": {
    "inputs": {
      "text": "",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "10": {
    "inputs": {
      "url": "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/input/example.png"
    },
    "class_type": "LoadImageFromUrl",
    "_meta": {
      "title": "Load Image From URL"
    }
  },
  "11": {
    "inputs": {
      "pixels": [
        "10",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
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
  },
   "save_image": {
    "inputs": {
      "filename_prefix": "comfy-bot-img-2-img-",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""

INSTANT_ID_BASIC = """
{
  "3": {
    "inputs": {
      "seed": 1631591050,
      "steps": 30,
      "cfg": 4.5,
      "sampler_name": "ddpm",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "60",
        0
      ],
      "positive": [
        "60",
        1
      ],
      "negative": [
        "60",
        2
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "sdxl\\\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "11": {
    "inputs": {
      "instantid_file": "ip-adapter.bin"
    },
    "class_type": "InstantIDModelLoader",
    "_meta": {
      "title": "Load InstantID Model"
    }
  },
  "16": {
    "inputs": {
      "control_net_name": "diffusion_pytorch_model.safetensors"
    },
    "class_type": "ControlNetLoader",
    "_meta": {
      "title": "Load ControlNet Model"
    }
  },
  "38": {
    "inputs": {
      "provider": "CPU"
    },
    "class_type": "InstantIDFaceAnalysis",
    "_meta": {
      "title": "InstantID Face Analysis"
    }
  },
  "39": {
    "inputs": {
      "text": "comic character. graphic illustration, comic art, graphic novel art, vibrant, highly detailed",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "40": {
    "inputs": {
      "text": "photograph, deformed, glitch, noisy, realistic, stock photo",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "60": {
    "inputs": {
      "weight": 0.8,
      "start_at": 0,
      "end_at": 1,
      "instantid": [
        "11",
        0
      ],
      "insightface": [
        "38",
        0
      ],
      "control_net": [
        "16",
        0
      ],
      "image": [
        "67",
        0
      ],
      "model": [
        "4",
        0
      ],
      "positive": [
        "39",
        0
      ],
      "negative": [
        "40",
        0
      ]
    },
    "class_type": "ApplyInstantID",
    "_meta": {
      "title": "Apply InstantID"
    }
  },
  "67": {
    "inputs": {
      "url": "https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/19b050360d36e076c33460dd327587561d23adcc/.meta/man.png"
    },
    "class_type": "LoadImageFromUrl",
    "_meta": {
      "title": "Load Image From URL"
    }
  },
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
  },
   "save_image": {
    "inputs": {
      "filename_prefix": "comfy-bot-instant-id-basic-",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""

INSTANT_ID_IP_ADAPTER ="""
{
  "3": {
    "inputs": {
      "seed": 19538649205350,
      "steps": 30,
      "cfg": 4.5,
      "sampler_name": "ddpm",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "74",
        0
      ],
      "positive": [
        "60",
        1
      ],
      "negative": [
        "60",
        2
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "sdxl\\\Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1536,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "11": {
    "inputs": {
      "instantid_file": "ip-adapter.bin"
    },
    "class_type": "InstantIDModelLoader",
    "_meta": {
      "title": "Load InstantID Model"
    }
  },
  "16": {
    "inputs": {
      "control_net_name": "diffusion_pytorch_model.safetensors"
    },
    "class_type": "ControlNetLoader",
    "_meta": {
      "title": "Load ControlNet Model"
    }
  },
  "38": {
    "inputs": {
      "provider": "CPU"
    },
    "class_type": "InstantIDFaceAnalysis",
    "_meta": {
      "title": "InstantID Face Analysis"
    }
  },
  "39": {
    "inputs": {
      "text": "a tiki god island",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "40": {
    "inputs": {
      "text": "photograph, deformed, glitch, noisy, realistic, stock photo",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "60": {
    "inputs": {
      "weight": 0.8,
      "start_at": 0,
      "end_at": 1,
      "instantid": [
        "11",
        0
      ],
      "insightface": [
        "38",
        0
      ],
      "control_net": [
        "16",
        0
      ],
      "image": [
        "75",
        0
      ],
      "model": [
        "4",
        0
      ],
      "positive": [
        "39",
        0
      ],
      "negative": [
        "40",
        0
      ]
    },
    "class_type": "ApplyInstantID",
    "_meta": {
      "title": "Apply InstantID"
    }
  },
  "72": {
    "inputs": {
      "weight": 1,
      "ipadapter": [
        "73",
        1
      ],
      "image": [
        "76",
        0
      ]
    },
    "class_type": "IPAdapterEncoder",
    "_meta": {
      "title": "IPAdapter Encoder"
    }
  },
  "73": {
    "inputs": {
      "preset": "PLUS (high strength)",
      "model": [
        "60",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoader",
    "_meta": {
      "title": "IPAdapter Unified Loader"
    }
  },
  "74": {
    "inputs": {
      "weight": 0.8,
      "weight_type": "linear",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "73",
        0
      ],
      "ipadapter": [
        "73",
        1
      ],
      "pos_embed": [
        "72",
        0
      ]
    },
    "class_type": "IPAdapterEmbeds",
    "_meta": {
      "title": "IPAdapter Embeds"
    }
  },
  "75": {
    "inputs": {
      "url": "https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/19b050360d36e076c33460dd327587561d23adcc/.meta/man.png"
    },
    "class_type": "LoadImageFromUrl",
    "_meta": {
      "title": "Face Image From URL"
    }
  },
  "76": {
    "inputs": {
      "url": "https://raw.githubusercontent.com/stavsap/ComfyUI-Discord-Bot/main/.meta/king.jpg"
    },
    "class_type": "LoadImageFromUrl",
    "_meta": {
      "title": "Style Image From URL"
    }
  },
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
  },
   "save_image": {
    "inputs": {
      "filename_prefix": "comfy-bot-instant-id-ip-adapter-face-",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""