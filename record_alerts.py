#!/usr/bin/env python3
"""
Record custom audio alerts for dog training
Allows you to record your own voice commands and alerts
"""

import pyaudio
import wave
import sys
from pathlib import Path

def record_audio(filename, duration=3):
    """Record audio from microphone"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    print(f"\n🎤 Recording {duration} seconds...")
    print("Speak now!")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("✓ Recording finished!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save to file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"💾 Saved: {filename}")

def play_audio(filename):
    """Play audio file to preview"""
    import platform
    import subprocess
    import os

    try:
        if platform.system() == 'Darwin':  # macOS
            os.system(f'afplay "{filename}"')
        elif platform.system() == 'Windows':
            os.system(f'start /min "" "{filename}"')
        else:  # Linux
            os.system(f'paplay "{filename}"')
    except:
        print("Could not play audio")

def main():
    print("\n" + "="*60)
    print("🎤 DontPiss - Custom Audio Alerts Recorder")
    print("="*60)

    # Create sounds directory
    sounds_dir = Path('sounds')
    sounds_dir.mkdir(exist_ok=True)

    alerts = [
        {
            'name': 'alert_soft',
            'prompt': 'Say a GENTLE warning (e.g., "Ei!", "Não!")',
            'duration': 2
        },
        {
            'name': 'alert_medium',
            'prompt': 'Say a FIRM command (e.g., "FORA!", "SAI DAÍ!")',
            'duration': 2
        },
        {
            'name': 'alert_strong',
            'prompt': 'Say a STRONG command (e.g., "SAI AGORA!", "FORA DAQUI!")',
            'duration': 3
        },
        {
            'name': 'good_dog',
            'prompt': 'Say praise (e.g., "Muito bem!", "Bom cachorro!")',
            'duration': 2
        }
    ]

    print("\nYou will record 4 audio alerts:")
    for i, alert in enumerate(alerts, 1):
        print(f"  {i}. {alert['name']}: {alert['prompt']}")

    input("\nPress ENTER when ready to start recording...")

    for i, alert in enumerate(alerts, 1):
        print(f"\n[{i}/{len(alerts)}] {alert['name']}")
        print(f"📝 {alert['prompt']}")

        filename = sounds_dir / f"{alert['name']}.wav"

        input("Press ENTER to record...")
        record_audio(str(filename), alert['duration'])

        # Preview
        while True:
            choice = input("\nPreview? (Y/n/redo): ").strip().lower()
            if choice == '' or choice == 'y':
                play_audio(str(filename))
                break
            elif choice == 'redo':
                print("\n🔄 Recording again...")
                record_audio(str(filename), alert['duration'])
            else:
                break

    print("\n" + "="*60)
    print("✅ All alerts recorded!")
    print("="*60)
    print("\nSaved files:")
    for alert in alerts:
        filename = sounds_dir / f"{alert['name']}.wav"
        if filename.exists():
            print(f"  ✓ {filename}")

    print("\n📖 These alerts will be used automatically in training modes.")
    print("   To re-record, run this script again.\n")

if __name__ == '__main__':
    try:
        import pyaudio
    except ImportError:
        print("\n❌ pyaudio not installed!")
        print("\nInstall it:")
        print("  Windows: pip install pyaudio")
        print("  macOS: pip install pyaudio")
        print("  Linux: sudo apt install python3-pyaudio && pip install pyaudio\n")
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
