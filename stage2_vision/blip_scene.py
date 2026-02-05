import torch
import warnings
import sys
import os
from contextlib import redirect_stdout, redirect_stderr
from transformers import BlipProcessor, BlipForConditionalGeneration
import cv2
from PIL import Image
import logging

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

_blip_model = None
_blip_processor = None


def get_blip_model():
    global _blip_model, _blip_processor
    if _blip_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Suppress all output during model loading
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with redirect_stdout(open(os.devnull, 'w')):
                with redirect_stderr(open(os.devnull, 'w')):
                    _blip_processor = BlipProcessor.from_pretrained(
                        "Salesforce/blip-image-captioning-base",
                        use_fast=False  # Avoid fast processor warning
                    )
                    _blip_model = BlipForConditionalGeneration.from_pretrained(
                        "Salesforce/blip-image-captioning-base",
                        tie_word_embeddings=False  # Avoid tie weights warning
                    ).to(device)
    return _blip_model, _blip_processor


def batch_process_frames(frames):
    """
    True batch processing for maximum speed
    """
    model, processor = get_blip_model()
    device = model.device
    
    # Prepare all frames at once
    batch_images = []
    for frame in frames:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        batch_images.append(image)
    
    # Process entire batch at once
    inputs = processor(batch_images, return_tensors="pt", padding=True).to(device)
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=20, num_beams=1)
        
    # Decode all results
    descriptions = []
    for output in outputs:
        description = processor.decode(output, skip_special_tokens=True)
        descriptions.append(description)
    
    return descriptions

def quick_classify(frame):
    """
    Quick classification without predefined labels (optimized)
    """
    model, processor = get_blip_model()
    device = model.device

    # Convert OpenCV → PIL
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame_rgb)

    # Generate description (optimized)
    inputs = processor(image, return_tensors="pt").to(device)
    
    with torch.no_grad():
        out = model.generate(**inputs, max_length=20, num_beams=1)  # Faster generation
        description = processor.decode(out[0], skip_special_tokens=True)
    
    return description
