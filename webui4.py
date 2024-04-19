import gradio as gr
import requests
import random
from datetime import datetime
from gradio import Textbox, Radio, Image
import numpy as np
import os

aspect_ratios = {
    "1:1": "1:1",
    "16:9": "16:9",
    "21:9": "21:9",
    "2:3": "2:3",
    "3:2": "3:2",
    "4:5": "4:5",
    "5:4": "5:4",
    "9:16": "9:16",
    "9:21": "9:21"
}

sdstyle_preset = {
    "3d-model": "3d-model",
    "analog-film": "analog-film",
    "anime": "anime",
    "cinematic": "cinematic",
    "comic-book": "comic-book",
    "digital-art": "digital-art",
    "fantasy-art":"fantasy-art",
    "isometric": "isometric",
    "line-art": "line-art",
    "low-poly": "low-poly",
    "modeling-compound": "modeling-compound",
    "neon-punk": "neon-punk",
    "origami": "origami",
    "photographic": "photographic",
    "pixel-art": "pixel-art",
    "tile-texture": "tile-texture"
}

def read_api_key(file_path):
    with open(file_path, "r") as file:
        api_key = file.read().strip()
    return api_key

def read_default_prompt(file_path):
    with open(file_path, "r") as file:
        default_prompt = file.read().strip()
    return default_prompt

def read_default_negative_prompt(file_path):
    with open(file_path, "r") as file:
        default_negative_prompt = file.read().strip()
    return default_negative_prompt

api_key = read_api_key("api.txt")
default_prompt = read_default_prompt("default_prompt.txt")
default_negative_prompt = read_default_negative_prompt("default_negative_prompt.txt")

def generate_image(prompt_in, negative_prompt_in, aspect_ratio_in, user_seed, choice, sdstyle):
    model_name = ""
    if not user_seed:
        user_seed = str(random.randint(0000000000, 4294967294))

    if choice == "SD3-turbo":
        model_name = "sd3-turbo"
        
    if choice == "SD3":
        model_name = "sd3"
        
    if choice == "Core":
        model_name = "core"
    
    if model_name == "sd3":
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "authorization": f"Bearer {api_key}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt_in,
                "negative_prompt": negative_prompt_in,
                "aspect_ratio": aspect_ratio_in,
                "model": model_name,
                "output_format": "jpeg",
                "seed": user_seed,
            },
        )
    elif model_name == "core":
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={
                "authorization": f"Bearer {api_key}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt_in,
                "negative_prompt": negative_prompt_in,
                "aspect_ratio": aspect_ratio_in,
                "style_preset": sdstyle_preset[sdstyle],
                "output_format": "jpeg",
                "seed": user_seed,
            },
        )
    
    else:
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "authorization": f"Bearer {api_key}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt_in,
                "aspect_ratio": aspect_ratio_in,
                "model": model_name,
                "output_format": "jpeg",
                "seed": user_seed,
            },
        )

    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if response.status_code == 200:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"output/{current_time}_seed_{user_seed}_{model_name}.jpeg"
        with open(output_name, 'wb') as file:
            file.write(response.content)
        return output_name
    else:
        raise Exception(str(response.json()))

iface = gr.Interface(fn=generate_image, 
                     inputs=[
                         Textbox(label="Prompt", value=default_prompt),
                         Textbox(label="Negative Prompt", value=default_negative_prompt),
                         Radio(list(aspect_ratios.keys()), label="Aspect Ratio", value="1:1"),
                         Textbox(label="Seed (Leave blank for random)"),
                         Radio(["SD3-turbo", "SD3", "Core"], label="Model Choice", value="SD3-turbo"),
                         Radio(list(sdstyle_preset.keys()), label="Core Style Choice", value="3d-model"),
                     ], 
                     outputs=Image(type="numpy"), 
                     allow_flagging="never",
                     title="SD3.0 Image Generator", 
                     description="Generate images via API using the Stable Diffusion 3.0 model.",
                     article="https://api.stability.ai/",
                     examples=[["Cute cat wearing a tophat", "Blurry, ugly", "1:1", "1234", "SD3-turbo"], ["Scruffy dog coming out of water", "Blurry, ugly", "16:9", "2468", "SD3"]])
iface.launch()
