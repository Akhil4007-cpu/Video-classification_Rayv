#!/usr/bin/env python3
"""
🚀 Smart Video Moderator - Quick Setup Script
Run this script to set up the environment automatically
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        print(f"✅ {description} completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    print("🎬 Smart Video Moderator - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            return
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # macOS/Linux
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    print(f"\n🔧 Installing dependencies...")
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python packages"):
        print("⚠️  Manual installation may be required")
        print("Run: pip install torch torchvision transformers ultralytics opencv-python mediapipe faster-whisper")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Test the system:")
    print("   python analyze_video.py \"path/to/your/video.mp4\"")
    print("\n📖 See README.md for detailed instructions")

if __name__ == "__main__":
    main()
