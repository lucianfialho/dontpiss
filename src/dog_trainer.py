#!/usr/bin/env python3
"""
Dog Trainer - Active training system with various alert methods
Extends zone_detector with training capabilities
"""

import subprocess
import os
import random
import time
import platform
from pathlib import Path


class DogTrainer:
    """Handles active training alerts for the dog"""

    def __init__(self, training_mode='gentle'):
        """
        Initialize trainer with specific mode

        Args:
            training_mode: 'gentle', 'standard', or 'intensive'
        """
        self.training_mode = training_mode
        self.last_alert_time = 0
        self.alert_count = 0

        # Training modes configuration
        self.modes = {
            'gentle': {
                'alert_delay': 2.0,  # Wait 2s before alerting
                'escalation': False,
                'repeat_alerts': 1,
                'volume': 'medium'
            },
            'standard': {
                'alert_delay': 0.5,  # Quick response
                'escalation': True,
                'repeat_alerts': 2,
                'volume': 'high'
            },
            'intensive': {
                'alert_delay': 0.0,  # Immediate
                'escalation': True,
                'repeat_alerts': 3,
                'volume': 'very_high'
            }
        }

        self.config = self.modes.get(training_mode, self.modes['standard'])

        # Sounds directory
        self.sounds_dir = Path(__file__).parent.parent / 'sounds'
        self.sounds_dir.mkdir(exist_ok=True)

    def play_beep(self, duration=0.3, frequency=800):
        """Play beep sound (cross-platform)"""
        try:
            if platform.system() == 'Darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Funk.aiff &')
            elif platform.system() == 'Windows':
                # Windows beep using winsound
                import winsound
                winsound.Beep(int(frequency), int(duration * 1000))
            else:  # Linux
                os.system(f'beep -f {frequency} -l {int(duration * 1000)} &')
        except Exception as e:
            # Fallback: just print (silent mode)
            pass

    def play_buzzer(self):
        """Play annoying buzzer sound"""
        try:
            if platform.system() == 'Darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Sosumi.aiff &')
            elif platform.system() == 'Windows':
                import winsound
                # Play sequence of annoying beeps
                for _ in range(3):
                    winsound.Beep(1000, 200)
                    time.sleep(0.1)
            else:  # Linux
                os.system('beep -f 1000 -l 200 -r 3 &')
        except:
            pass

    def play_voice_command(self, command="No"):
        """Play voice command using text-to-speech (cross-platform)"""
        try:
            commands = {
                "No": ["No!", "Off!", "Down!", "Get down!"],
                "Warning": ["Don't even think about it!", "I'm watching you!"],
                "Good": ["Good dog!", "Well done!"]
            }

            message = random.choice(commands.get(command, ["No!"]))

            if platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['say', '-v', 'Samantha', '-r', '200', message],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system() == 'Windows':
                # Use PowerShell's text-to-speech (non-blocking)
                ps_command = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{message}")'
                subprocess.Popen(['powershell', '-Command', ps_command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0)
            else:  # Linux
                subprocess.Popen(['espeak', message],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            # Silent fallback
            pass

    def play_ultrasonic_simulation(self):
        """
        Simulate ultrasonic deterrent with high-frequency beeps
        (Dogs hear higher frequencies than humans)
        """
        try:
            if platform.system() == 'Darwin':  # macOS
                for _ in range(3):
                    os.system('afplay /System/Library/Sounds/Tink.aiff &')
                    time.sleep(0.1)
            elif platform.system() == 'Windows':
                import winsound
                # Play high-frequency beeps
                for _ in range(3):
                    winsound.Beep(3000, 100)  # High pitch
                    time.sleep(0.1)
            else:  # Linux
                os.system('beep -f 3000 -l 100 -r 3 &')
        except:
            pass

    def escalate_alert(self, violation_duration):
        """Escalate alert based on how long dog has been in zone"""

        if violation_duration < 1:
            # Level 1: Gentle warning (first second)
            self.play_beep(duration=0.2)

        elif violation_duration < 3:
            # Level 2: Firm warning (1-3 seconds)
            self.play_voice_command("No")

        elif violation_duration < 5:
            # Level 3: Strong deterrent (3-5 seconds)
            self.play_buzzer()
            self.play_voice_command("No")

        else:
            # Level 4: Maximum deterrent (5+ seconds)
            self.play_ultrasonic_simulation()
            self.play_voice_command("No")
            self.play_buzzer()

    def alert(self, frames_in_zone):
        """
        Main alert method

        Args:
            frames_in_zone: Number of consecutive frames dog has been in zone
        """
        current_time = time.time()

        # Calculate violation duration in seconds (assuming 30 fps)
        violation_duration = frames_in_zone / 30.0

        # Check if enough time has passed since last alert
        if current_time - self.last_alert_time < self.config['alert_delay']:
            return

        self.last_alert_time = current_time
        self.alert_count += 1

        # Different alert strategies based on mode
        if self.config['escalation']:
            # Escalating alerts based on duration
            self.escalate_alert(violation_duration)
        else:
            # Simple repeated alert
            for _ in range(self.config['repeat_alerts']):
                self.play_beep(duration=0.3)
                time.sleep(0.2)

    def positive_reinforcement(self):
        """Play positive sound when dog leaves zone"""
        try:
            # Play pleasant sound
            os.system('afplay /System/Library/Sounds/Hero.aiff')
            # Optional: voice praise
            if random.random() < 0.3:  # 30% of the time
                self.play_voice_command("Good")
        except:
            pass

    def get_stats(self):
        """Get training session statistics"""
        return {
            'mode': self.training_mode,
            'alerts_triggered': self.alert_count,
            'config': self.config
        }


def create_training_sounds():
    """
    Helper function to create custom training sounds
    You can record your own sounds and place them in sounds/ directory
    """
    sounds_dir = Path(__file__).parent.parent / 'sounds'
    sounds_dir.mkdir(exist_ok=True)

    readme = sounds_dir / 'README.md'
    with open(readme, 'w') as f:
        f.write("""# Custom Training Sounds

Place your custom sound files here:

- `alert.wav` - Main alert sound
- `warning.wav` - Warning sound
- `good.wav` - Positive reinforcement sound
- `buzzer.wav` - Strong deterrent sound

## Recommended sounds:

1. **Alert**: Short beep or whistle
2. **Warning**: Your voice saying "No!" or "Off!"
3. **Good**: Your voice saying "Good dog!"
4. **Buzzer**: Loud buzzer or horn

## Recording tips:

- Use `.wav` or `.aiff` format
- Keep files short (< 2 seconds)
- Record at moderate volume
- Clear, distinct sounds work best

## macOS text-to-speech:

You can create voice files:
```bash
say -o alert.aiff "No! Get down!"
say -o good.aiff "Good dog! Well done!"
```
""")

    print(f"📁 Sounds directory created: {sounds_dir}")
    print(f"📄 See {readme} for instructions")


if __name__ == "__main__":
    # Demo of different training modes
    print("🎓 Dog Trainer Demo\n")

    modes = ['gentle', 'standard', 'intensive']

    for mode in modes:
        print(f"\n{'='*50}")
        print(f"Mode: {mode.upper()}")
        print(f"{'='*50}")

        trainer = DogTrainer(training_mode=mode)

        print(f"Config: {trainer.config}")
        print("\nSimulating alerts...")

        # Simulate escalating violation
        for frames in [15, 60, 150, 300]:
            print(f"  Frames in zone: {frames} (~{frames/30:.1f}s)")
            trainer.alert(frames)
            time.sleep(1)

        stats = trainer.get_stats()
        print(f"\nStats: {stats}")

    print("\n✅ Demo complete!")
    print("\nTo create custom sounds:")
    print("  Run: python -c 'from dog_trainer import create_training_sounds; create_training_sounds()'")
