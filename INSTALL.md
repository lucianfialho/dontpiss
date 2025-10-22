# 🔧 Installation Guide

## Python Version Compatibility

**Recommended:** Python 3.9 - 3.11 (best compatibility)

| Python Version | Status | Notes |
|---------------|--------|-------|
| 3.8 | ✅ Supported | Minimum version |
| 3.9 | ✅ Recommended | Best compatibility |
| 3.10 | ✅ Recommended | Best compatibility |
| 3.11 | ✅ Supported | Works well |
| 3.12 | ⚠️ Limited | PyTorch may have issues |
| 3.13+ | ❌ Not supported | PyTorch not available yet |

---

## Installation Methods

### Method 1: Standard Installation (Python 3.9-3.11)

```bash
# 1. Create virtual environment
python3.11 -m venv venv  # or python3.10, python3.9
source venv/bin/activate

# 2. Install requirements
pip install -r requirements.txt
```

### Method 2: Minimal Installation (Older/Slower Machines)

For older computers or if you have Python version issues:

```bash
# 1. Check Python version
python3 --version

# 2. If Python 3.13+, install Python 3.11
# macOS:
brew install python@3.11

# 3. Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# 4. Install minimal requirements
pip install -r requirements-minimal.txt
```

### Method 3: Without PyTorch (Ultra-minimal)

If PyTorch installation fails:

```bash
# Install dependencies one by one
pip install opencv-python
pip install numpy==1.24.0
pip install ultralytics  # This will install PyTorch automatically
pip install pillow
pip install plyer
```

---

## Troubleshooting

### Error: "Could not find a version that satisfies the requirement torch"

**Cause:** Python 3.13 or newer

**Solution:**
```bash
# 1. Check Python version
python --version

# 2. Install Python 3.11
# macOS:
brew install python@3.11

# Ubuntu/Debian:
sudo apt install python3.11 python3.11-venv

# 3. Create new venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# 4. Verify version
python --version  # Should show 3.11.x

# 5. Install requirements
pip install -r requirements-minimal.txt
```

### Error: "Building wheel for opencv-python failed"

**Cause:** Missing system dependencies or old CPU

**Solution 1 - Use prebuilt binaries:**
```bash
pip install --only-binary :all: opencv-python
```

**Solution 2 - Install headless version (lighter):**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

**Solution 3 - System dependencies (Linux):**
```bash
sudo apt-get update
sudo apt-get install python3-opencv
pip install opencv-python --no-build-isolation
```

### Error: "numpy version conflict"

**Solution:**
```bash
pip install "numpy>=1.21.0,<2.0.0"
```

### Slow Installation

For slower/older machines:

```bash
# Use pip with cache
pip install --cache-dir=/tmp/pip-cache -r requirements-minimal.txt

# Or install one by one with progress
pip install opencv-python --verbose
pip install numpy==1.24.0 --verbose
pip install ultralytics --verbose
```

---

## System Requirements

### Minimum
- **CPU:** Intel Core i3 or equivalent
- **RAM:** 4GB (8GB recommended)
- **Storage:** 2GB free space
- **OS:** macOS 10.14+, Ubuntu 18.04+, Windows 10+
- **Camera:** Any webcam or IP camera

### Recommended
- **CPU:** Intel Core i5 or better
- **RAM:** 8GB or more
- **Storage:** 5GB free space
- **GPU:** Optional (NVIDIA GPU with CUDA support)
- **Camera:** 720p or better

---

## Platform-Specific Instructions

### macOS

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Python 3.11
brew install python@3.11

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install requirements
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

### Ubuntu/Debian Linux

```bash
# 1. Update system
sudo apt-get update
sudo apt-get upgrade

# 2. Install Python 3.11 and dependencies
sudo apt-get install python3.11 python3.11-venv python3.11-dev
sudo apt-get install python3-pip
sudo apt-get install libopencv-dev

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install requirements
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

### Windows

```powershell
# 1. Download Python 3.11 from python.org
# Install with "Add to PATH" checked

# 2. Open PowerShell or Command Prompt
cd path\to\dontpiss

# 3. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install requirements
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

---

## Raspberry Pi (ARM Devices)

For Raspberry Pi 4 or newer:

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install python3-opencv python3-numpy
sudo apt-get install libatlas-base-dev

# 2. Create virtual environment
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 3. Install remaining packages
pip install ultralytics
pip install pillow
pip install plyer
```

**Note:** YOLO on Raspberry Pi will be slower. Consider using:
- Lower resolution camera (640x480)
- YOLOv8n (nano) model only
- Reduce FPS to 10-15

---

## Verification

After installation, verify everything works:

```bash
# 1. Activate environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Test imports
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "from ultralytics import YOLO; print('Ultralytics: OK')"

# 3. Run quick test
python quick_zone_setup.py
```

If all imports work, you're ready!

---

## Optional Components

### Analytics (Charts and Graphs)

```bash
pip install pandas matplotlib seaborn
```

### Desktop Notifications (macOS)

```bash
pip install pyobjus
```

Or disable in `src/config.py`:
```python
NOTIFICATIONS = {
    'desktop_notification': False
}
```

---

## Upgrading

To upgrade to the latest versions:

```bash
# Activate environment
source venv/bin/activate

# Upgrade all packages
pip install --upgrade -r requirements.txt

# Or upgrade specific package
pip install --upgrade ultralytics
```

---

## Fresh Install

If you want to start clean:

```bash
# 1. Remove old environment
rm -rf venv/

# 2. Remove pip cache
rm -rf ~/.cache/pip/

# 3. Start fresh
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

---

## Docker (Advanced)

For consistent environment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-minimal.txt .

RUN apt-get update && \
    apt-get install -y libopencv-dev && \
    pip install -r requirements-minimal.txt

COPY . .

CMD ["python", "src/zone_detector.py"]
```

```bash
docker build -t dontpiss .
docker run --device /dev/video0 dontpiss
```

---

## Getting Help

If installation fails:

1. **Check Python version:** `python --version`
2. **Check pip version:** `pip --version` (should be 20.0+)
3. **Update pip:** `pip install --upgrade pip`
4. **Try minimal install:** Use `requirements-minimal.txt`
5. **Check logs:** Look for specific error messages
6. **Open issue:** https://github.com/lucianfialho/dontpiss/issues

Include in issue:
- OS and version
- Python version
- Full error message
- Output of `pip list`

---

## Quick Reference

```bash
# Standard install (Python 3.9-3.11)
python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Minimal install (older machines)
python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements-minimal.txt

# Without PyTorch (manual)
pip install opencv-python numpy ultralytics pillow plyer

# Verify
python -c "from ultralytics import YOLO; import cv2; print('All good!')"
```

---

**Need help?** Open an issue on GitHub with your system details!
