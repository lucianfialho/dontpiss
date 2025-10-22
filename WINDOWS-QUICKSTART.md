# 🪟 Windows Quick Start (5 minutes)

**Skip Docker on Windows - use native Python instead.**

## 1. Check Python Version

```powershell
# Check your Python version
python --version
```

**You need Python 3.9, 3.10, or 3.11** (NOT 3.12, 3.13, or 3.14)

If you have Python 3.12+:
```powershell
# Install Python 3.11 from Microsoft Store
winget install Python.Python.3.11

# Or download from:
# https://www.python.org/downloads/release/python-3110/
# ✅ CHECK "Add Python to PATH" during installation
```

## 2. Setup Project

```powershell
# Open PowerShell in the project folder
cd C:\Users\Arklok\dontpiss

# Create virtual environment with Python 3.11
py -3.11 -m venv venv
# Or if only one Python installed:
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies (use Windows-specific requirements)
pip install --upgrade pip
pip install -r requirements-windows.txt
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

You have Python 3.12+ which needs compilation. **Install Python 3.11 instead:**

```powershell
# Remove old venv
Remove-Item -Recurse -Force venv

# Install Python 3.11
winget install Python.Python.3.11

# Create new venv with 3.11
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements-windows.txt
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
