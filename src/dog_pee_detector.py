#!/usr/bin/env python3
"""
DontPiss - Dog Pee Detection System
Main detection script using computer vision and pose estimation
"""

import cv2
import numpy as np
import logging
import time
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

import config
from pose_analyzer import PoseAnalyzer
from notifier import Notifier


class DogPeeDetector:
    """Main detector class for monitoring dog urination"""

    def __init__(self, config_module):
        self.config = config_module
        self.load_user_config()
        self.setup_logging()

        # Initialize components
        self.pose_analyzer = PoseAnalyzer(config_module)
        self.notifier = Notifier(config_module)

        # Initialize model
        self.model = None
        self.setup_model()

        # Video capture
        self.cap = None

    def load_user_config(self):
        """Load user configuration from setup wizard"""
        user_config_file = Path(__file__).parent.parent / 'user_config.json'

        if user_config_file.exists():
            try:
                with open(user_config_file, 'r') as f:
                    user_config = json.load(f)

                # Override config with user preferences
                if 'camera_index' in user_config:
                    self.config.CAMERA_INDEX = user_config['camera_index']

                if 'detection_profile' in user_config:
                    profile = user_config['detection_profile']
                    self.config.PEE_DETECTION['min_frames_threshold'] = profile.get('min_frames_threshold', 15)
                    self.config.PEE_DETECTION['leg_lift_angle_threshold'] = profile.get('leg_lift_angle_threshold', 45)
                    self.config.PEE_DETECTION['squat_height_ratio'] = profile.get('squat_height_ratio', 0.5)

                if 'notifications' in user_config:
                    notif = user_config['notifications']
                    self.config.NOTIFICATIONS['sound'] = notif.get('sound', True)
                    self.config.NOTIFICATIONS['desktop_notification'] = notif.get('desktop_notification', True)
                    self.config.NOTIFICATIONS['save_snapshot'] = notif.get('save_snapshot', True)

                print(f"✅ Configuração do usuário carregada: {user_config_file}")

            except Exception as e:
                print(f"⚠️  Erro ao carregar configuração do usuário: {e}")
                print("   Usando configuração padrão...")
        else:
            print("ℹ️  Nenhuma configuração personalizada encontrada.")
            print("   Execute 'python setup.py' para configurar câmera e preferências.")

    def setup_logging(self):
        """Configure logging"""
        log_dir = Path(self.config.LOG_FILE).parent
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_model(self):
        """Initialize pose estimation model"""
        self.logger.info(f"Loading model: {self.config.MODEL_TYPE}")

        try:
            if self.config.MODEL_TYPE == "yolo":
                from ultralytics import YOLO
                self.model = YOLO(self.config.YOLO_MODEL)
                self.logger.info("YOLO model loaded successfully")
            else:
                self.logger.error(f"Unsupported model type: {self.config.MODEL_TYPE}")
                raise ValueError("Only 'yolo' model type is currently supported")

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.logger.info("Attempting to download model...")
            try:
                from ultralytics import YOLO
                # This will download the model if not present
                self.model = YOLO('yolov8n-pose.pt')
                self.logger.info("Model downloaded and loaded successfully")
            except Exception as e2:
                self.logger.error(f"Failed to download model: {e2}")
                raise

    def setup_camera(self):
        """Initialize camera/video source"""
        self.logger.info(f"Initializing camera: {self.config.CAMERA_INDEX}")

        if isinstance(self.config.CAMERA_INDEX, str):
            # Video file
            self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        else:
            # Camera index
            self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.FPS)

        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera/video source")

        self.logger.info("Camera initialized successfully")

    def draw_skeleton(self, frame, keypoints):
        """Draw skeleton and keypoints on frame"""
        if keypoints is None or len(keypoints) == 0:
            return frame

        # Define skeleton connections (pairs of keypoint indices)
        skeleton = [
            (0, 1), (0, 2),  # nose to eyes
            (1, 3), (2, 4),  # eyes to ears
            (5, 6),  # shoulders
            (5, 7), (7, 9),  # left front leg
            (6, 8), (8, 10),  # right front leg
            (5, 11), (6, 12),  # shoulders to hips
            (11, 12),  # hips
            (11, 13), (13, 15),  # left back leg
            (12, 14), (14, 16),  # right back leg
            (11, 17), (17, 18),  # tail
        ]

        # Draw skeleton
        for start_idx, end_idx in skeleton:
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_point = keypoints[start_idx][:2].astype(int)
                end_point = keypoints[end_idx][:2].astype(int)

                # Only draw if confidence is high enough
                if keypoints[start_idx][2] > 0.3 and keypoints[end_idx][2] > 0.3:
                    cv2.line(frame, tuple(start_point), tuple(end_point),
                            (0, 255, 0), 2)

        # Draw keypoints
        for i, kp in enumerate(keypoints):
            if kp[2] > 0.3:  # confidence threshold
                x, y = int(kp[0]), int(kp[1])
                cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)

        return frame

    def check_humans_nearby(self, result, dog_keypoints):
        """Check if there are humans near the dog"""
        if not self.config.PEE_DETECTION.get('ignore_with_humans_nearby', False):
            return False

        # YOLOv8-pose detects multiple poses, check if any are human-sized
        if not hasattr(result, 'keypoints') or result.keypoints is None:
            return False

        if len(result.keypoints.data) <= 1:
            return False  # Only dog detected

        # Get dog position
        dog_x = dog_keypoints[:, 0].mean()
        dog_y = dog_keypoints[:, 1].mean()

        threshold = self.config.PEE_DETECTION['human_proximity_threshold']
        frame_width = result.orig_shape[1] if hasattr(result, 'orig_shape') else 1280

        # Check other detected poses
        for i in range(1, len(result.keypoints.data)):
            other_kp = result.keypoints.data[i].cpu().numpy()
            other_x = other_kp[:, 0].mean()
            other_y = other_kp[:, 1].mean()

            # Calculate distance
            distance = abs(other_x - dog_x)
            if distance < (frame_width * threshold):
                return True  # Human nearby

        return False

    def process_frame(self, frame, current_time):
        """Process a single frame"""
        # Run pose estimation
        results = self.model(frame, conf=self.config.CONFIDENCE_THRESHOLD, verbose=False)

        keypoints = None
        detection_result = None
        humans_nearby = False

        # Process results
        if results and len(results) > 0:
            result = results[0]

            # Check if any dogs detected
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                # Get first detection (assuming single dog)
                if len(result.keypoints.data) > 0:
                    keypoints = result.keypoints.data[0].cpu().numpy()

                    # Check for humans nearby
                    humans_nearby = self.check_humans_nearby(result, keypoints)

                    # Analyze pose for pee detection
                    detection_result = self.pose_analyzer.analyze_pose(
                        keypoints, current_time, humans_nearby
                    )

                    # Draw skeleton if enabled
                    if self.config.DISPLAY['show_skeleton']:
                        frame = self.draw_skeleton(frame, keypoints)

        return frame, keypoints, detection_result

    def draw_info(self, frame, detection_result, fps):
        """Draw detection information on frame"""
        if not self.config.DISPLAY['show_detection_info']:
            return frame

        # Draw FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Draw detection status
        if detection_result and detection_result['is_peeing']:
            status = "PEEING DETECTED!"
            color = (0, 0, 255)  # Red
            cv2.putText(frame, status, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
            cv2.putText(frame, f"Type: {detection_result['detection_type']}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(frame, f"Conf: {detection_result['confidence']:.2%}", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        else:
            status = "Monitoring..."
            color = (0, 255, 0)  # Green
            cv2.putText(frame, status, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            if detection_result and detection_result['frames_detected'] > 0:
                frames = detection_result['frames_detected']
                threshold = self.config.PEE_DETECTION['min_frames_threshold']
                cv2.putText(frame, f"Detecting: {frames}/{threshold}", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Draw debug info if enabled
        if self.config.DISPLAY.get('debug_mode', False) and detection_result:
            self.draw_debug_info(frame, detection_result)

        return frame

    def draw_debug_info(self, frame, detection_result):
        """Draw detailed debug information"""
        if 'debug' not in detection_result:
            return

        debug = detection_result['debug']
        height, width = frame.shape[:2]

        # Create semi-transparent overlay panel
        overlay = frame.copy()
        panel_x = width - 350
        panel_y = 10
        panel_width = 340
        panel_height = 200

        cv2.rectangle(overlay, (panel_x, panel_y),
                     (panel_x + panel_width, panel_y + panel_height),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw debug text
        y_offset = panel_y + 25
        line_height = 25
        text_color = (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5

        # Title
        cv2.putText(frame, "DEBUG INFO", (panel_x + 10, y_offset),
                   font, 0.6, (0, 255, 255), 2)
        y_offset += line_height

        # Leg lift
        leg_color = (0, 255, 0) if debug['leg_lift_detected'] else (100, 100, 100)
        cv2.putText(frame, f"Leg Lift: {debug['leg_lift_confidence']:.2%}",
                   (panel_x + 10, y_offset), font, font_scale, leg_color, 1)
        y_offset += line_height

        # Squat
        squat_color = (0, 255, 0) if debug['squat_detected'] else (100, 100, 100)
        cv2.putText(frame, f"Squat: {debug['squat_confidence']:.2%}",
                   (panel_x + 10, y_offset), font, font_scale, squat_color, 1)
        y_offset += line_height

        # Tail
        tail_color = (0, 255, 0) if debug['tail_raised'] else (100, 100, 100)
        cv2.putText(frame, f"Tail Raised: {debug['tail_raised']}",
                   (panel_x + 10, y_offset), font, font_scale, tail_color, 1)
        y_offset += line_height

        # Counter with progress bar
        counter = debug['detection_counter']
        min_frames = debug['min_frames_needed']
        cv2.putText(frame, f"Frames: {counter}/{min_frames}",
                   (panel_x + 10, y_offset), font, font_scale, text_color, 1)
        y_offset += line_height

        # Progress bar
        bar_width = 300
        bar_height = 20
        progress = min(counter / min_frames, 1.0) if min_frames > 0 else 0
        bar_x = panel_x + 20
        bar_y = y_offset

        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     (50, 50, 50), -1)

        # Progress bar
        if progress > 0:
            bar_color = (0, 255, 0) if progress >= 1.0 else (0, 255, 255)
            cv2.rectangle(frame, (bar_x, bar_y),
                         (bar_x + int(bar_width * progress), bar_y + bar_height),
                         bar_color, -1)

        # Border
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     (255, 255, 255), 1)

    def run(self):
        """Main detection loop"""
        self.logger.info("Starting DontPiss detection system...")
        self.setup_camera()

        print("\n" + "=" * 60)
        print("DontPiss - Dog Pee Detection System")
        print("=" * 60)
        print("Press 'q' to quit")
        print("Press 's' to save current frame")
        print("Press 'r' to reset detection")
        print("Press 'd' to toggle debug mode")
        print("=" * 60 + "\n")

        frame_count = 0
        start_time = time.time()
        fps = 0

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.warning("Failed to read frame")
                    break

                current_time = time.time()
                frame_count += 1

                # Calculate FPS
                if frame_count % 30 == 0:
                    fps = 30 / (current_time - start_time)
                    start_time = current_time

                # Process frame
                processed_frame, keypoints, detection_result = self.process_frame(
                    frame, current_time
                )

                # Check for pee detection
                if detection_result and detection_result['is_peeing']:
                    self.notifier.notify(processed_frame, detection_result)

                # Draw information
                processed_frame = self.draw_info(processed_frame, detection_result, fps)

                # Display frame
                if self.config.DISPLAY['show_video']:
                    cv2.imshow('DontPiss - Dog Pee Detector', processed_frame)

                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("Quit requested")
                    break
                elif key == ord('s'):
                    timestamp = time.strftime('%Y%m%d_%H%M%S')
                    filename = f"manual_snapshot_{timestamp}.jpg"
                    cv2.imwrite(f"data/{filename}", processed_frame)
                    self.logger.info(f"Snapshot saved: {filename}")
                elif key == ord('r'):
                    self.pose_analyzer.reset_detection()
                    self.logger.info("Detection reset")
                elif key == ord('d'):
                    self.config.DISPLAY['debug_mode'] = not self.config.DISPLAY.get('debug_mode', False)
                    status = "ON" if self.config.DISPLAY['debug_mode'] else "OFF"
                    self.logger.info(f"Debug mode: {status}")
                    print(f"\n🔧 Debug mode: {status}\n")

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.logger.info("Shutdown complete")


def main():
    """Entry point"""
    try:
        detector = DogPeeDetector(config)
        detector.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
