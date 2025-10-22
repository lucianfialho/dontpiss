# 🐕 DontPiss - AI Dog Training System

**Smart computer vision system to train your dog not to jump on furniture using real-time alerts and progressive training.**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)

## 🎯 What is DontPiss?

DontPiss is an AI-powered dog training system that uses computer vision to detect when your dog enters forbidden zones (like your sofa) and automatically triggers training alerts to discourage the behavior.

### Key Features

- 🎥 **Real-time Detection** - Instantly detects when dog enters forbidden zones
- 🔊 **Active Training** - Automated audio alerts and voice commands
- 📊 **Progress Analytics** - Track training effectiveness over time
- 🎓 **Multiple Training Modes** - Gentle, Standard, Intensive, and Silent modes
- ✅ **Positive Reinforcement** - Rewards when dog leaves the zone
- 📈 **Data-Driven** - Analyze patterns and optimize training strategy

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/dontpiss.git
cd dontpiss

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Forbidden Zone

```bash
# Run quick setup to draw zone on your sofa
python quick_zone_setup.py
```

**Instructions:**
- Click and drag to draw a rectangle over your sofa
- Press 'S' to save
- Done!

### 3. Start Training

```bash
cd src
python zone_detector.py --mode standard
```

That's it! The system will now:
- Detect when your dog jumps on the sofa
- Play audio alerts and voice commands
- Log all violations for analysis
- Provide positive reinforcement when dog leaves

## 🎓 Training Modes

### Gentle Mode
Perfect for sensitive dogs or starting training.
```bash
python zone_detector.py --mode gentle
```
- 2-second delay before alerting
- Soft beeps only
- No escalation

### Standard Mode ⭐ (Recommended)
Balanced approach for most dogs.
```bash
python zone_detector.py --mode standard
```
- Quick 0.5s response
- Progressive alerts (beep → voice → buzzer)
- Moderate intensity

### Intensive Mode
For stubborn cases.
```bash
python zone_detector.py --mode intensive
```
- Immediate response
- Aggressive escalation
- Multiple repeated alerts
- **Use with caution**

### Silent Mode
Monitoring only, no alerts.
```bash
python zone_detector.py --mode silent
```
- Logs violations only
- Perfect for already-trained dogs
- Data collection

## 📊 Analytics & Progress Tracking

Monitor your dog's training progress:

```bash
# View text report
python analyze_training.py

# Generate charts
python analyze_training.py --charts
```

### What You Get:
- Total violations and daily breakdown
- Hourly patterns (when dog misbehaves most)
- Week-over-week improvement percentage
- Visual charts and graphs
- Trend analysis

**Example Output:**
```
📊 TRAINING REPORT
Total violations: 145
Period: 7 days
Average per day: 20.7
Improvement: 71.4% ✅

Week 1: 35 violations/day
Week 2: 10 violations/day
```

## 🏗️ Project Structure

```
dontpiss/
├── src/
│   ├── zone_detector.py      # Main detection + training system
│   ├── dog_trainer.py         # Training alert logic
│   ├── dog_pee_detector.py    # Pose-based detection (legacy)
│   ├── pose_analyzer.py       # Pose analysis utilities
│   ├── notifier.py            # Notification system
│   └── config.py              # Configuration
├── quick_zone_setup.py        # Quick zone configuration
├── setup_zone.py              # Advanced zone setup
├── analyze_training.py        # Analytics tool
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── README_ZONE.md             # Zone detection details
├── README_TRAINING.md         # Training guide
├── README_ANALYTICS.md        # Analytics guide
└── TROUBLESHOOTING.md         # Common issues
```

## 🔧 How It Works

1. **Computer Vision Detection**
   - Uses YOLOv8 to detect dogs in real-time
   - Tracks dog position via bounding boxes
   - ~30 FPS on modern hardware

2. **Zone Violation Detection**
   - Checks if dog's center point is inside forbidden zone
   - Requires 5 consecutive frames (0.15s) to confirm
   - Prevents false positives from quick movements

3. **Training Alerts**
   - Progressive escalation based on violation duration
   - 0-1s: Soft beep
   - 1-3s: Voice command ("No!", "Off!")
   - 3-5s: Buzzer + voice
   - 5s+: Multiple intense alerts

4. **Positive Reinforcement**
   - Pleasant sound when dog leaves zone
   - Voice praise ("Good dog!") randomly
   - Reinforces correct behavior

5. **Data Logging**
   - Every violation logged with timestamp
   - CSV format for easy analysis
   - Snapshots saved automatically

## 📖 Documentation

- [🚫 Zone Detection Guide](README_ZONE.md) - How zone detection works
- [🎓 Training Guide](README_TRAINING.md) - Complete training strategies
- [📊 Analytics Guide](README_ANALYTICS.md) - Understanding your data
- [🔧 Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## 🎯 Training Strategy

### Week 1-2: Introduction (Gentle Mode)
- Dog is learning the concept
- Expect 20-30 violations/day
- Be patient and consistent

### Week 3-4: Reinforcement (Standard Mode)
- Dog understands but testing limits
- Expect 10-15 violations/day
- Stay consistent

### Week 5+: Maintenance
- Well-trained behavior
- Expect < 5 violations/day
- Can switch to Silent mode for monitoring

### Success Metrics
- **< 3 violations/day for 7 consecutive days = TRAINED! 🎉**

## 🔊 Customization

### Portuguese Voice Commands

Edit `src/dog_trainer.py`:
```python
commands = {
    "No": ["Não!", "Fora!", "Sai daí!"],
    "Good": ["Muito bem!", "Bom cachorro!"]
}
```

### Custom Audio Files

Place your own audio files in `sounds/` directory:
- `alert.wav` - Custom alert sound
- `good.wav` - Custom praise sound

### macOS Text-to-Speech

```bash
# Create custom voice alerts
say -o sounds/alert.aiff "Get off the sofa now!"
say -o sounds/good.aiff "Good dog!"
```

## 💡 Tips for Success

### ✅ Do's
- Use the same mode consistently for 1-2 weeks
- Provide comfortable alternative (dog bed nearby)
- Reward manually when dog ignores sofa
- Run system 24/7 for best results
- Analyze data weekly to track progress

### ❌ Don'ts
- Don't switch modes frequently
- Don't manually punish (let system handle it)
- Don't give up after a few days
- Don't use Intensive mode long-term without breaks

## 🛠️ Requirements

- Python 3.8+
- Webcam or IP camera
- macOS, Linux, or Windows
- ~2GB RAM
- Modern CPU (GPU optional)

## 📦 Dependencies

- OpenCV - Computer vision
- Ultralytics YOLO - Object detection
- PyTorch - Deep learning backend
- Pandas - Data analysis
- Matplotlib - Visualization
- NumPy - Numerical computing

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Support for more animal species (cats, etc.)
- Mobile app integration
- Cloud storage for analytics
- Multi-camera support
- Voice assistant integration (Alexa, Google Home)

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- Inspired by pet training psychology research
- Community feedback and testing

## 🐛 Issues & Support

Found a bug or need help?
- Check [Troubleshooting Guide](TROUBLESHOOTING.md)
- Open an issue on GitHub
- Include: OS, Python version, dog breed/size, error logs

## 📊 Project Status

- ✅ Core detection working
- ✅ Zone configuration
- ✅ Training modes
- ✅ Analytics system
- ✅ Documentation
- 🔄 Mobile app (planned)
- 🔄 Multi-camera support (planned)
- 🔄 Cloud sync (planned)

## 🌟 Star History

If this project helps train your dog, give it a star! ⭐

---

**Made with 🐕 and Python**

*DontPiss - Because prevention is better than cleanup!*
