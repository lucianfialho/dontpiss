# 🐳 Docker Setup Guide

Run DontPiss in Docker for consistent environment across any machine.

## Quick Start

### 1. Install Docker

**macOS:**
```bash
brew install --cask docker
# Or download from https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

**Windows:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and restart computer
3. Enable WSL 2 backend when prompted
4. Open PowerShell or Command Prompt

### 2. Configure Forbidden Zone

**macOS/Linux:**
```bash
# Run zone setup container
docker-compose --profile setup run --rm zone-setup
```

**Windows (PowerShell):**
```powershell
# Run zone setup container
docker-compose --profile setup run --rm zone-setup
```

- Click and drag to draw rectangle over sofa
- Press 'S' to save
- Press 'Q' to quit

### 3. Start Detection

**macOS/Linux:**
```bash
# Build and start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Windows (PowerShell):**
```powershell
# Build and start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Usage

### Different Training Modes

**Gentle Mode:**
```bash
docker-compose run --rm dontpiss python src/zone_detector.py --mode gentle
```

**Standard Mode (default):**
```bash
docker-compose up -d
```

**Intensive Mode:**
```bash
docker-compose run --rm dontpiss python src/zone_detector.py --mode intensive
```

**Silent Mode (monitoring only):**
```bash
docker-compose run --rm dontpiss python src/zone_detector.py --mode silent
```

### Analytics

```bash
# View training report
docker-compose run --rm dontpiss python analyze_training.py

# Generate charts
docker-compose run --rm dontpiss python analyze_training.py --charts
```

## Docker Commands Reference

```bash
# Build image
docker-compose build

# Start in background
docker-compose up -d

# View logs (live)
docker-compose logs -f

# Stop container
docker-compose stop

# Stop and remove container
docker-compose down

# Restart
docker-compose restart

# Run one-off command
docker-compose run --rm dontpiss python src/zone_detector.py --help

# Check if running
docker-compose ps

# View resource usage
docker stats dontpiss
```

## Troubleshooting

### Camera Not Found

**Linux:**
```bash
# Find your camera device
ls -l /dev/video*

# If it's /dev/video1 instead of /dev/video0, edit docker-compose.yml:
devices:
  - /dev/video1:/dev/video0
```

**macOS:**
```bash
# Docker Desktop needs camera access
# System Preferences → Privacy & Security → Camera → Docker Desktop
```

**Windows:**
1. Open Docker Desktop Settings
2. Go to Resources → WSL Integration
3. Enable integration with your WSL distro
4. Camera access:
   - Settings → Privacy → Camera
   - Allow Docker Desktop to access camera
5. If using USB camera:
   ```powershell
   # Check if camera is detected in Windows
   # Device Manager → Imaging devices
   ```
6. For WSL 2, you may need USB passthrough:
   - Install usbipd-win: `winget install usbipd`
   - Attach camera to WSL:
     ```powershell
     # In PowerShell (as Administrator)
     usbipd wsl list
     usbipd wsl attach --busid <BUSID>
     ```

**USB Camera (all platforms):**
```bash
# Make sure camera is connected before starting container
docker-compose down
docker-compose up -d
```

### Display Issues (X11 on Linux)

```bash
# Allow Docker to access display
xhost +local:docker

# Run with display
DISPLAY=:0 docker-compose up -d

# After testing, secure it:
xhost -local:docker
```

### Permission Denied on /dev/video0

**Linux:**
```bash
# Add user to video group
sudo usermod -aG video $USER

# Or run with privileged mode (edit docker-compose.yml):
privileged: true
```

### Model Download Failed

```bash
# Download models manually first
docker-compose run --rm dontpiss python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Then start normally
docker-compose up -d
```

### Container Keeps Restarting

```bash
# Check logs for errors
docker-compose logs

# Run interactively to debug
docker-compose run --rm dontpiss bash
python src/zone_detector.py --mode standard
```

## Data Persistence

All data is stored in volumes on your host machine:

```
dontpiss/
├── data/           # Snapshots
├── logs/           # Violation logs
├── analytics/      # Charts and reports
├── sounds/         # Custom audio files
└── zone_config.json  # Zone configuration
```

Even if you delete the container, your data persists.

## Custom Configuration

### Use Different Camera Source

Edit `docker-compose.yml`:
```yaml
environment:
  - CAMERA_SOURCE=1  # Use camera index 1
  # Or for IP camera:
  - CAMERA_SOURCE=rtsp://192.168.1.100/stream
```

### Limit Resources

Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # Max 2 CPU cores
      memory: 2G     # Max 2GB RAM
```

### Auto-start on Boot

```bash
# Set restart policy
docker-compose up -d

# Container will auto-start when Docker starts
```

## Raspberry Pi (ARM)

For Raspberry Pi 4 or newer:

```bash
# Use ARM-compatible base image
# Edit Dockerfile first line to:
FROM python:3.11-slim-bullseye

# Build
docker-compose build --no-cache

# Start
docker-compose up -d
```

**Note:** YOLO will be slower on ARM. Consider:
- Using YOLOv8n (nano) only
- Reducing camera resolution
- Limiting FPS

## Multi-Container Setup

Run multiple cameras/zones:

```yaml
# docker-compose.yml
services:
  dontpiss-living-room:
    build: .
    container_name: dontpiss-living-room
    devices:
      - /dev/video0:/dev/video0
    volumes:
      - ./configs/living-room:/app/config
      - ./data/living-room:/app/data
    environment:
      - TRAINING_MODE=standard

  dontpiss-bedroom:
    build: .
    container_name: dontpiss-bedroom
    devices:
      - /dev/video1:/dev/video0
    volumes:
      - ./configs/bedroom:/app/config
      - ./data/bedroom:/app/data
    environment:
      - TRAINING_MODE=gentle
```

## Updating

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Uninstalling

**macOS/Linux:**
```bash
# Stop and remove containers
docker-compose down

# Remove image
docker rmi dontpiss-dontpiss

# Remove all data (WARNING: permanent!)
rm -rf data/ logs/ analytics/ sounds/ zone_config.json
```

**Windows (PowerShell):**
```powershell
# Stop and remove containers
docker-compose down

# Remove image
docker rmi dontpiss-dontpiss

# Remove all data (WARNING: permanent!)
Remove-Item -Recurse -Force data, logs, analytics, sounds, zone_config.json
```

## Performance Tips

1. **Use specific Python version** - Already using 3.11-slim
2. **Cache pip packages** - Already optimized in Dockerfile
3. **Minimize image size** - Using slim base image (~150MB)
4. **Layer caching** - Requirements copied before code
5. **Clean apt cache** - Done in Dockerfile

## Security

```bash
# Run as non-root user (edit Dockerfile):
RUN useradd -m -u 1000 dontpiss
USER dontpiss

# Drop capabilities
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - CAP_VIDEO  # Only camera access
```

## Backup

```bash
# Backup all data
tar -czf dontpiss-backup-$(date +%Y%m%d).tar.gz \
    data/ logs/ analytics/ sounds/ zone_config.json

# Restore
tar -xzf dontpiss-backup-20240101.tar.gz
```

## Monitoring

```bash
# Watch logs live
docker-compose logs -f --tail=100

# Resource usage
docker stats dontpiss

# Export logs
docker-compose logs > dontpiss-logs.txt
```

## Why Docker?

✅ **Benefits:**
- No Python version conflicts
- Same environment everywhere
- Easy deployment to other machines
- Isolated dependencies
- Simple updates
- Resource limiting
- Auto-restart on crash

❌ **Trade-offs:**
- Slightly higher resource usage (~200MB overhead)
- Learning curve if new to Docker
- Camera access can be tricky on some systems

---

**Recommended:** Use Docker for production deployment, regular Python for development.
