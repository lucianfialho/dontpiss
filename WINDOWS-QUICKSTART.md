# 🪟 Windows Quick Start (5 minutes)

**Skip Docker on Windows - use native Python instead.**

## 1. Install Python

```powershell
# Check if you have Python
python --version
```

If not installed or too old:
```powershell
# Install latest Python from Microsoft Store (easiest)
winget install Python.Python.3.12

# Or download from python.org
# ✅ CHECK "Add Python to PATH" during installation
```

## 2. Setup Project

```powershell
# Open PowerShell

# Clone repository (if you don't have it)
git clone https://github.com/lucianfialho/dontpiss.git
cd dontpiss

# Or just navigate to it
cd C:\Users\SEU_USUARIO\dontpiss

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-windows.txt
```

**Note:** If numpy installation fails, try:
```powershell
pip install numpy --only-binary :all:
```

## 3. Configure Zone

```powershell
# Still with venv activated
python quick_zone_setup.py
```

**Instructions:**
- Webcam will open showing your room
- Click and drag a rectangle around your sofa
- Press **'S'** to save
- Press **'Q'** to quit

## 4. Start Training

```powershell
cd src
python zone_detector.py --mode standard
```

Done! 🎉

---

## Troubleshooting

### "Python not found"

```powershell
# Install Python 3.11 from Microsoft Store
winget install Python.Python.3.11
```

### "Camera not found"

```powershell
# Open Windows Camera app first to test
# Then try different camera index:
python zone_detector.py --camera 1
```

### "Module not found"

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
venv\Scripts\activate

# Reinstall
pip install -r requirements-windows.txt
```

### "numpy build failed" or "compiler not found"

Try installing pre-built wheel only:

```powershell
# Use only pre-built binaries (no compilation)
pip install numpy --only-binary :all:
pip install opencv-python --only-binary :all:
pip install ultralytics
```

If still fails, you can skip analytics and use core only:
```powershell
pip install opencv-python numpy ultralytics pillow plyer
```

---

## Daily Use

```powershell
# Every time you want to run:
cd C:\Users\Arklok\dontpiss
venv\Scripts\activate
cd src
python zone_detector.py --mode standard
```

---

## View Training Progress

```powershell
# From project root
python analyze_training.py

# With charts
python analyze_training.py --charts
```

---

**Why not Docker on Windows?**

Docker has camera access issues on Windows. Native Python is:
- ✅ Easier to setup (no WSL, no USB passthrough)
- ✅ Works with built-in laptop cameras
- ✅ Better performance
- ✅ Simpler troubleshooting
