#!/usr/bin/env python3
"""
DontPiss Setup Wizard
Interactive setup for first-time configuration
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("🐕 DontPiss - Setup Wizard")
    print("="*60 + "\n")

def print_step(step, total, message):
    print(f"[{step}/{total}] {message}")

def test_camera():
    """Test if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        cap.release()
        return ret
    except Exception as e:
        print(f"   Error: {e}")
        return False

def download_models():
    """Download YOLO models"""
    try:
        from ultralytics import YOLO
        # This will download the model if not present
        model = YOLO('yolov8n.pt')
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

def check_zone_configured():
    """Check if zone is already configured"""
    possible_paths = [
        Path('zone_config.json'),
        Path('src/zone_config.json')
    ]
    for path in possible_paths:
        if path.exists():
            return True
    return False

def run_zone_setup():
    """Run the zone setup script"""
    try:
        print("\n   Opening camera to configure forbidden zone...")
        print("   Instructions:")
        print("   - Click and drag to draw rectangle around sofa")
        print("   - Press 'S' to save")
        print("   - Press 'Q' to quit\n")

        result = subprocess.run([sys.executable, 'quick_zone_setup.py'],
                              capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"   Error: {e}")
        return False

def choose_training_mode():
    """Let user choose training mode"""
    print("\n   Choose training mode:")
    print("   1. Gentle     - Soft alerts, 2s delay (for sensitive dogs)")
    print("   2. Standard   - Balanced approach (RECOMMENDED)")
    print("   3. Intensive  - Aggressive alerts, immediate response")
    print("   4. Silent     - Monitoring only, no alerts")

    while True:
        choice = input("\n   Enter choice (1-4) [default: 2]: ").strip()
        if not choice:
            return 'standard'
        if choice == '1':
            return 'gentle'
        elif choice == '2':
            return 'standard'
        elif choice == '3':
            return 'intensive'
        elif choice == '4':
            return 'silent'
        else:
            print("   Invalid choice. Please enter 1-4.")

def start_detector(mode='standard'):
    """Start the zone detector"""
    try:
        print(f"\n   Starting detector in {mode} mode...")
        print("   Press Ctrl+C to stop\n")

        os.chdir('src')
        subprocess.run([sys.executable, 'zone_detector.py', '--mode', mode])
    except KeyboardInterrupt:
        print("\n\n✓ Detector stopped.")
    except Exception as e:
        print(f"\n   Error: {e}")

def main():
    print_header()

    # Step 1: Check dependencies
    print_step(1, 5, "Checking dependencies...")
    try:
        import cv2
        import numpy
        from ultralytics import YOLO
        print("   ✓ All dependencies installed")
    except ImportError as e:
        print(f"   ✗ Missing dependency: {e}")
        print("\n   Please run: pip install -r requirements-windows.txt")
        return 1

    # Step 2: Test camera
    print_step(2, 5, "Testing camera access...")
    if test_camera():
        print("   ✓ Camera is working")
    else:
        print("   ✗ Camera not accessible")
        print("\n   Troubleshooting:")
        print("   - Check if camera is connected")
        print("   - Close other apps using camera")
        print("   - Try different camera index in config")

        choice = input("\n   Continue anyway? (y/N): ").strip().lower()
        if choice != 'y':
            return 1

    # Step 3: Download models
    print_step(3, 5, "Downloading YOLO models (if needed)...")
    if download_models():
        print("   ✓ Models ready")
    else:
        print("   ✗ Failed to download models")
        return 1

    # Step 4: Configure zone
    print_step(4, 5, "Configuring forbidden zone...")

    if check_zone_configured():
        print("   ℹ Zone already configured")
        reconfigure = input("   Reconfigure zone? (y/N): ").strip().lower()
        if reconfigure == 'y':
            if run_zone_setup():
                print("   ✓ Zone configured")
            else:
                print("   ✗ Zone setup failed")
                return 1
        else:
            print("   ✓ Using existing zone configuration")
    else:
        if run_zone_setup():
            print("   ✓ Zone configured")
        else:
            print("   ✗ Zone setup cancelled or failed")
            choice = input("\n   Continue without zone? (y/N): ").strip().lower()
            if choice != 'y':
                return 1

    # Step 5: Choose mode and start
    print_step(5, 5, "Ready to start training!")

    mode = choose_training_mode()

    print("\n" + "="*60)
    print("✓ Setup Complete!")
    print("="*60)
    print(f"\nMode: {mode.upper()}")
    print("Logs will be saved to: logs/violations.csv")
    print("Snapshots will be saved to: data/snapshots/")
    print("\nTo view analytics later, run:")
    print("  python analyze_training.py")
    print("="*60 + "\n")

    start_now = input("Start detector now? (Y/n): ").strip().lower()
    if start_now != 'n':
        start_detector(mode)
    else:
        print("\nTo start manually later, run:")
        print(f"  cd src")
        print(f"  python zone_detector.py --mode {mode}")

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
