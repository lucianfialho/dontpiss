"""
Notification system for dog pee detection alerts
"""

import os
import logging
import time
from datetime import datetime
from pathlib import Path
import cv2

logger = logging.getLogger(__name__)


class Notifier:
    """Handles notifications when dog urination is detected"""

    def __init__(self, config):
        self.config = config
        self.notification_config = config.NOTIFICATIONS

        # Create directories if they don't exist
        if self.notification_config['save_snapshot']:
            os.makedirs(self.notification_config['snapshot_dir'], exist_ok=True)

        # Try to import notification library
        self.desktop_available = False
        if self.notification_config['desktop_notification']:
            try:
                from plyer import notification
                self.notification = notification
                self.desktop_available = True
            except ImportError:
                logger.warning("plyer not installed. Desktop notifications disabled.")
                logger.info("Install with: pip install plyer")

    def play_sound(self):
        """Play alert sound"""
        if not self.notification_config['sound']:
            return

        try:
            # Try different sound methods based on platform
            import platform
            system = platform.system()

            if system == 'Darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Glass.aiff')
            elif system == 'Linux':
                os.system('paplay /usr/share/sounds/freedesktop/stereo/bell.oga')
            elif system == 'Windows':
                import winsound
                winsound.MessageBeep()
        except Exception as e:
            logger.warning(f"Could not play sound: {e}")

    def show_desktop_notification(self, detection_info: dict):
        """Show desktop notification"""
        if not self.notification_config['desktop_notification'] or not self.desktop_available:
            return

        try:
            title = "Dog Pee Detection Alert!"
            message = (
                f"Type: {detection_info['detection_type']}\n"
                f"Confidence: {detection_info['confidence']:.2%}\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}"
            )

            self.notification.notify(
                title=title,
                message=message,
                app_name='DontPiss',
                timeout=10
            )
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")

    def save_snapshot(self, frame, detection_info: dict):
        """Save snapshot of the detection"""
        if not self.notification_config['save_snapshot']:
            return None

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            detection_type = detection_info['detection_type']
            confidence = int(detection_info['confidence'] * 100)

            filename = f"pee_detected_{detection_type}_{confidence}pct_{timestamp}.jpg"
            filepath = os.path.join(
                self.notification_config['snapshot_dir'],
                filename
            )

            cv2.imwrite(filepath, frame)
            logger.info(f"Snapshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return None

    def log_detection(self, detection_info: dict, snapshot_path: str = None):
        """Log detection to file"""
        try:
            log_file = Path('logs/detections.csv')
            log_file.parent.mkdir(exist_ok=True)

            # Create header if file doesn't exist
            if not log_file.exists():
                with open(log_file, 'w') as f:
                    f.write('timestamp,detection_type,confidence,snapshot_path\n')

            # Append detection
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(
                    f"{timestamp},"
                    f"{detection_info['detection_type']},"
                    f"{detection_info['confidence']:.4f},"
                    f"{snapshot_path or 'N/A'}\n"
                )
        except Exception as e:
            logger.error(f"Failed to log detection: {e}")

    def notify(self, frame, detection_info: dict):
        """
        Main notification method - triggers all enabled notifications
        Args:
            frame: Current video frame
            detection_info: Dictionary with detection details
        """
        if not self.notification_config['enabled']:
            return

        logger.info(
            f"DETECTION! Type: {detection_info['detection_type']}, "
            f"Confidence: {detection_info['confidence']:.2%}"
        )

        # Save snapshot
        snapshot_path = self.save_snapshot(frame, detection_info)

        # Log detection
        self.log_detection(detection_info, snapshot_path)

        # Play sound
        self.play_sound()

        # Show desktop notification
        self.show_desktop_notification(detection_info)

        # Print to console
        print("\n" + "=" * 50)
        print("🐕 PEE DETECTION ALERT!")
        print(f"Type: {detection_info['detection_type'].upper()}")
        print(f"Confidence: {detection_info['confidence']:.2%}")
        print(f"Frames: {detection_info['frames_detected']}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if snapshot_path:
            print(f"Snapshot: {snapshot_path}")
        print("=" * 50 + "\n")
