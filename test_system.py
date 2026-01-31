#!/usr/bin/env python3
"""
🧪 Smart Video Moderator - Test Script
Quick test to verify the system is working correctly
"""

import os
import sys
import time

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    try:
        import transformers
        print("✅ Transformers imported successfully")
    except ImportError:
        print("❌ Transformers not installed")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    
    try:
        import mediapipe
        print("✅ MediaPipe imported successfully")
    except ImportError:
        print("❌ MediaPipe not installed")
        return False
    
    return True

def test_blip_model():
    """Test BLIP model loading"""
    print("\n🧠 Testing BLIP model...")
    
    try:
        from stage2_vision.blip_scene import get_blip_model
        model, processor = get_blip_model()
        print("✅ BLIP model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ BLIP model loading failed: {e}")
        return False

def test_basic_analysis():
    """Test basic video analysis with a sample frame"""
    print("\n🎬 Testing basic analysis...")
    
    try:
        import cv2
        import numpy as np
        from stage2_vision.blip_only import detect_objects_blip_only, classify_scene_blip_only
        from stage2_vision.blip_scene import load_labels
        
        # Create a simple test frame (black image)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test object detection
        risky, safe = detect_objects_blip_only([test_frame])
        print(f"✅ Object detection test passed: risky={risky}, safe={safe}")
        
        # Test scene classification
        labels = load_labels("config/clip_labels.txt")
        scene_results, scene_types = classify_scene_blip_only([test_frame], labels)
        print(f"✅ Scene classification test passed: scene_types={scene_types}")
        
        return True
    except Exception as e:
        print(f"❌ Basic analysis test failed: {e}")
        return False

def main():
    print("🧪 Smart Video Moderator - System Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return
    
    # Test BLIP model
    if not test_blip_model():
        print("\n❌ BLIP model test failed. Check model installation.")
        return
    
    # Test basic analysis
    if not test_basic_analysis():
        print("\n❌ Basic analysis test failed. Check configuration.")
        return
    
    print("\n🎉 All tests passed! System is ready to use.")
    print("\n📋 Try analyzing a video:")
    print("python analyze_video.py \"path/to/your/video.mp4\"")

if __name__ == "__main__":
    main()
