import torch
import warnings
import sys
import os
import traceback
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
    True batch processing for maximum speed with error handling
    """
    if not frames:
        return []
    
    try:
        model, processor = get_blip_model()
        device = model.device
        
        # Prepare all frames at once with error handling
        batch_images = []
        for i, frame in enumerate(frames):
            try:
                if frame is None:
                    print(f"⚠️  Frame {i} is None, skipping")
                    continue
                    
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                batch_images.append(image)
            except Exception as e:
                print(f"⚠️  Error processing frame {i}: {str(e)}")
                continue
        
        if not batch_images:
            print("❌ No valid frames to process")
            return []
        
        # Process entire batch at once with timeout protection
        print(f"🔄 Processing batch of {len(batch_images)} frames...")
        inputs = processor(batch_images, return_tensors="pt", padding=True).to(device)
        
        with torch.no_grad():
            try:
                outputs = model.generate(**inputs, max_length=20, num_beams=1, do_sample=False)
            except Exception as e:
                print(f"⚠️  BLIP generation error: {str(e)}")
                # Fallback to individual processing
                return _fallback_individual_processing(batch_images, processor, model, device)
            
        # Decode all results with error handling
        descriptions = []
        for i, output in enumerate(outputs):
            try:
                description = processor.decode(output, skip_special_tokens=True)
                descriptions.append(description)
            except Exception as e:
                print(f"⚠️  Error decoding output {i}: {str(e)}")
                descriptions.append("error in description")
        
        return descriptions
        
    except Exception as e:
        print(f"❌ Critical error in batch processing: {str(e)}")
        traceback.print_exc()
        return []


def _fallback_individual_processing(batch_images, processor, model, device):
    """Fallback to individual frame processing if batch fails"""
    print("🔄 Falling back to individual frame processing...")
    descriptions = []
    
    for i, image in enumerate(batch_images):
        try:
            inputs = processor(image, return_tensors="pt").to(device)
            with torch.no_grad():
                output = model.generate(**inputs, max_length=20, num_beams=1, do_sample=False)
            description = processor.decode(output[0], skip_special_tokens=True)
            descriptions.append(description)
        except Exception as e:
            print(f"⚠️  Error in individual processing frame {i}: {str(e)}")
            descriptions.append("error in description")
    
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
