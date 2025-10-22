# 🪟 Windows Setup Guide

Complete guide for running DontPiss on Windows.

## Option 1: Native Python (Recommended for Windows)

Docker has camera access limitations on Windows. **Native Python is easier on Windows.**

### Quick Setup

```powershell
# 1. Install Python 3.11
# Download from: https://www.python.org/downloads/
# ✅ Check "Add Python to PATH" during installation

# 2. Clone repository
git clone https://github.com/lucianfialho/dontpiss.git
cd dontpiss

# 3. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements-minimal.txt

# 5. Setup zone
python quick_zone_setup.py

# 6. Start training
cd src
python zone_detector.py --mode standard
```

### Troubleshooting

**Camera not detected:**
```powershell
# Check if camera is working
# Open Windows Camera app first to test

# Try different camera index
python zone_detector.py --camera 0
# or
python zone_detector.py --camera 1
```

**Python not found:**
```powershell
# Install Python 3.11 from Microsoft Store
winget install Python.Python.3.11

# Or download from python.org
```

**Module not found:**
```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements-minimal.txt
```

---

## Option 2: Docker on Windows (Advanced)

Docker on Windows has camera access limitations. This works but requires extra setup.

### Requirements

1. Windows 10/11 Pro or Enterprise (for Hyper-V)
2. WSL 2 enabled
3. Docker Desktop installed
4. USB camera (built-in laptop cameras may not work)

### Setup Steps

#### 1. Install Docker Desktop

```powershell
# Download Docker Desktop
# https://www.docker.com/products/docker-desktop

# Or install via winget
winget install Docker.DockerDesktop
```

Restart computer after installation.

#### 2. Enable WSL 2

```powershell
# Open PowerShell as Administrator

# Enable WSL
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2

# Restart computer
```

#### 3. Install USB Passthrough (for USB cameras)

```powershell
# Install usbipd (as Administrator)
winget install usbipd

# List USB devices
usbipd list

# Find your camera (look for "Imaging" or camera name)
# Note the BUSID (e.g., 2-3)

# Attach camera to WSL
usbipd bind --busid 2-3
usbipd attach --wsl --busid 2-3
```

#### 4. Run with Windows Config

```powershell
# Clone repository
git clone https://github.com/lucianfialho/dontpiss.git
cd dontpiss

# Use Windows-specific compose file
docker-compose -f docker-compose.yml -f docker-compose.windows.yml --profile setup run --rm zone-setup

# Start training
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.windows.yml logs -f
```

### Docker Troubleshooting

**Error: no such file or directory "/dev/video0"**

This is normal on Windows. Use the Windows compose file:
```powershell
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up
```

**Camera not working in Docker:**

1. Check camera works in Windows:
   - Open Camera app
   - Take a photo to verify

2. Try native Python instead (easier):
   ```powershell
   # Exit Docker
   docker-compose down

   # Use native Python (see Option 1 above)
   ```

3. For USB cameras with Docker:
   ```powershell
   # Check USB device in WSL
   usbipd list

   # Attach to WSL
   usbipd attach --wsl --busid <YOUR-BUSID>

   # Verify in WSL
   wsl
   ls /dev/video*
   exit
   ```

**Docker Desktop not starting:**

1. Enable virtualization in BIOS
2. Enable Hyper-V:
   ```powershell
   # As Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```
3. Restart computer

**WSL 2 errors:**

```powershell
# Update WSL
wsl --update

# Set default version
wsl --set-default-version 2

# Check WSL status
wsl --status
```

---

## Option 3: Direct Python (No Virtual Environment)

If you have issues with virtual environments:

```powershell
# Install Python 3.11 from python.org

# Install dependencies globally
pip install opencv-python numpy ultralytics pillow plyer

# Run setup
python quick_zone_setup.py

# Run detector
cd src
python zone_detector.py --mode standard
```

---

## Performance Tips for Windows

1. **Close unnecessary programs** - Free up RAM and CPU
2. **Use Power Plan: High Performance**
   - Control Panel → Power Options → High Performance
3. **Disable Windows Defender real-time scanning** (temporarily)
   - Settings → Privacy & Security → Windows Security → Virus & threat protection
4. **Use USB camera instead of built-in** - Better compatibility
5. **Lower resolution if needed** - Edit `src/config.py`:
   ```python
   CAMERA_RESOLUTION = (640, 480)  # Lower resolution
   ```

---

## Running as Windows Service (Advanced)

To run DontPiss automatically on startup:

### Using Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `C:\Users\YourUser\dontpiss\venv\Scripts\python.exe`
6. Arguments: `C:\Users\YourUser\dontpiss\src\zone_detector.py --mode standard`
7. Start in: `C:\Users\YourUser\dontpiss\src`

### Using NSSM (Non-Sucking Service Manager)

```powershell
# Download NSSM
# https://nssm.cc/download

# Install service
nssm install DontPiss "C:\Users\YourUser\dontpiss\venv\Scripts\python.exe" "C:\Users\YourUser\dontpiss\src\zone_detector.py --mode standard"

# Start service
nssm start DontPiss

# Check status
nssm status DontPiss
```

---

## Recommended: Native Python

**For Windows, we recommend native Python over Docker** because:

✅ **Pros:**
- Easier camera access (no USB passthrough needed)
- Better performance (no virtualization overhead)
- Simpler setup (no WSL 2, Docker Desktop, etc.)
- Works with built-in laptop cameras
- Faster startup

❌ **Docker Cons on Windows:**
- Camera access is complicated (needs USB passthrough)
- Requires WSL 2, Hyper-V, Docker Desktop
- Built-in cameras often don't work
- Slower performance
- More complex troubleshooting

---

## Quick Reference

### Native Python Commands

```powershell
# Activate environment
venv\Scripts\activate

# Setup zone
python quick_zone_setup.py

# Run detector
cd src
python zone_detector.py --mode standard

# View analytics
cd ..
python analyze_training.py

# Check logs
type logs\violations.csv
```

### Docker Commands (if using)

```powershell
# Setup zone
docker-compose -f docker-compose.yml -f docker-compose.windows.yml --profile setup run --rm zone-setup

# Start
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d

# Stop
docker-compose -f docker-compose.yml -f docker-compose.windows.yml down

# Logs
docker-compose -f docker-compose.yml -f docker-compose.windows.yml logs -f
```

---

## Getting Help

If you have issues:

1. **Try native Python first** (Option 1) - it's easier on Windows
2. Check camera works in Windows Camera app
3. Make sure Python 3.11 is installed (not 3.13)
4. Check antivirus isn't blocking camera access
5. Open issue on GitHub with error details

---

**Recommendation:** Use native Python installation (Option 1) for Windows. Docker is better for Linux/macOS.
