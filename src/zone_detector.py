#!/usr/bin/env python3
"""
Zone Detector - Simple dog detection in forbidden zones (like sofa)
Much simpler and more accurate than pose-based detection
"""

import cv2
import numpy as np
import json
import logging
import time
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

import config
from notifier import Notifier
from dog_trainer import DogTrainer


class ZoneDetector:
    """Detects when dog enters forbidden zones"""

    def __init__(self, training_mode='standard', enable_trainer=True):
        # Initialize zones list first (will be populated by load_zones)
        self.zones = []

        self.setup_logging()
        self.load_zones()  # This populates self.zones
        self.load_user_config()

        # Initialize components
        self.notifier = Notifier(config)

        # Initialize trainer for active alerts
        self.enable_trainer = enable_trainer
        if enable_trainer:
            self.trainer = DogTrainer(training_mode=training_mode)
            self.logger.info(f"Trainer initialized in '{training_mode}' mode")
        else:
            self.trainer = None

        # Initialize YOLO for object detection (not pose)
        self.setup_model()

        # Detection state
        self.last_alert_time = 0
        self.alert_cooldown = 30  # seconds
        self.frames_in_zone = 0
        self.min_frames_threshold = 5  # ~0.15s at 30fps (quick detection)
        self.was_in_zone = False  # Track if dog just left zone

        # Video capture
        self.cap = None

    def setup_logging(self):
        """Configure logging"""
        log_dir = Path(config.LOG_FILE).parent
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/zone_detector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_zones(self):
        """Load forbidden zones from config"""
        # Try multiple locations for zone config
        possible_paths = [
            Path(__file__).parent / 'zone_config.json',  # src/zone_config.json
            Path(__file__).parent.parent / 'zone_config.json',  # ../zone_config.json
            Path('zone_config.json'),  # ./zone_config.json
        ]

        zone_config_file = None
        for path in possible_paths:
            print(f"🔍 Procurando: {path.absolute()}")
            if path.exists():
                zone_config_file = path
                print(f"✅ Encontrado: {zone_config_file.absolute()}")
                break

        if zone_config_file is None:
            self.logger.error("Zone config not found in any location!")
            print("\n❌ Nenhuma zona configurada!")
            print("Procurei em:")
            for path in possible_paths:
                print(f"  - {path.absolute()}")
            print("\nExecute: python quick_zone_setup.py\n")
            sys.exit(1)

        try:
            self.logger.info(f"Loading zones from: {zone_config_file.absolute()}")
            with open(zone_config_file, 'r') as f:
                zone_config = json.load(f)
                self.zones = zone_config.get('zones', [])
                self.camera_index = zone_config.get('camera_index', 0)

            self.logger.info(f"Loaded {len(self.zones)} zone(s)")
            print(f"📋 Carregadas {len(self.zones)} zona(s) de: {zone_config_file}")

            for zone in self.zones:
                self.logger.info(f"  - {zone['name']}: {zone['type']}")

        except Exception as e:
            self.logger.error(f"Failed to load zones: {e}")
            print(f"\n❌ Erro ao carregar zonas: {e}")
            sys.exit(1)

    def load_user_config(self):
        """Load user configuration"""
        user_config_file = Path(__file__).parent.parent / 'user_config.json'

        if user_config_file.exists():
            try:
                with open(user_config_file, 'r') as f:
                    user_config = json.load(f)
                    if 'camera_index' in user_config:
                        self.camera_index = user_config['camera_index']
            except Exception as e:
                self.logger.warning(f"Could not load user config: {e}")

    def setup_model(self):
        """Initialize YOLO model for object detection"""
        self.logger.info("Loading YOLO model...")

        try:
            from ultralytics import YOLO
            # Use regular detection model (faster than pose)
            self.model = YOLO('yolov8n.pt')  # nano model
            self.logger.info("YOLO model loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def setup_camera(self):
        """Initialize camera/video source"""
        self.logger.info(f"Initializing camera: {self.camera_index}")

        if isinstance(self.camera_index, str):
            self.cap = cv2.VideoCapture(self.camera_index)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera/video source")

        self.logger.info("Camera initialized successfully")

    def point_in_polygon(self, point, polygon):
        """Check if point is inside polygon using ray casting"""
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def check_dog_in_zones(self, boxes):
        """Check if any detected dog is in forbidden zone"""
        if boxes is None or len(boxes) == 0:
            return None

        for zone in self.zones:
            zone_points = zone['points']

            # Check each detected object
            for box in boxes:
                # Get box center point
                x1, y1, x2, y2 = box[:4]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # Check if center is in zone
                if self.point_in_polygon((center_x, center_y), zone_points):
                    return {
                        'zone': zone,
                        'box': box,
                        'center': (center_x, center_y)
                    }

        return None

    def process_frame(self, frame, current_time):
        """Process a single frame"""
        # Run object detection
        results = self.model(frame, conf=0.4, verbose=False)

        dog_boxes = []
        violation = None

        # Process results
        if results and len(results) > 0:
            result = results[0]

            if hasattr(result, 'boxes') and result.boxes is not None:
                # Filter for dogs (class 16 in COCO dataset)
                for box in result.boxes:
                    cls = int(box.cls[0])
                    if cls == 16:  # dog class
                        dog_boxes.append(box.xyxy[0].cpu().numpy())

        # Check if dog in forbidden zone
        if dog_boxes:
            violation = self.check_dog_in_zones(dog_boxes)

            if violation:
                self.frames_in_zone += 1
            else:
                self.frames_in_zone = 0

        # Check if alert threshold met
        should_alert = False
        if self.frames_in_zone >= self.min_frames_threshold:
            time_since_last = current_time - self.last_alert_time
            if time_since_last > self.alert_cooldown:
                should_alert = True
                self.last_alert_time = current_time

        return frame, dog_boxes, violation, should_alert

    def draw_zones(self, frame):
        """Draw forbidden zones on frame"""
        overlay = frame.copy()

        # Debug: show zone count
        cv2.putText(frame, f"Zonas: {len(self.zones)}", (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if len(self.zones) == 0:
            cv2.putText(frame, "NENHUMA ZONA CONFIGURADA!", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            return frame

        for zone in self.zones:
            points = np.array(zone['points'], dtype=np.int32)
            color = tuple(zone['color'])

            # Fill zone with transparency
            cv2.fillPoly(overlay, [points], color)

            # Draw border (thicker for visibility)
            cv2.polylines(frame, [points], True, color, 5)

            # Draw zone name
            x, y = zone['points'][0]
            cv2.putText(frame, zone['name'], (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)

        # Blend overlay with more opacity for visibility
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        return frame

    def draw_detections(self, frame, dog_boxes, violation):
        """Draw dog detections"""
        for box in dog_boxes:
            x1, y1, x2, y2 = map(int, box[:4])

            # Color: red if in zone, green otherwise
            color = (0, 0, 255) if violation else (0, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, "DOG", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Draw violation marker
        if violation:
            cx, cy = violation['center']
            cv2.circle(frame, (cx, cy), 10, (0, 0, 255), -1)
            cv2.circle(frame, (cx, cy), 15, (0, 0, 255), 2)

        return frame

    def draw_info(self, frame, violation, fps):
        """Draw detection information"""
        # Draw FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Draw status
        if violation:
            status = "ZONA PROIBIDA INVADIDA!"
            color = (0, 0, 255)
            cv2.putText(frame, status, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

            zone_name = violation['zone']['name']
            cv2.putText(frame, f"Zona: {zone_name}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Progress bar
            progress = min(self.frames_in_zone / self.min_frames_threshold, 1.0)
            cv2.putText(frame, f"Frames: {self.frames_in_zone}/{self.min_frames_threshold}",
                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            status = "Monitorando..."
            color = (0, 255, 0)
            cv2.putText(frame, status, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        return frame

    def run(self):
        """Main detection loop"""
        self.logger.info("Starting Zone Detector...")
        self.setup_camera()

        print("\n" + "=" * 60)
        print("🚫 Zone Detector - Detecção de Zona Proibida")
        print("=" * 60)
        print(f"Zonas configuradas: {len(self.zones)}")

        if len(self.zones) == 0:
            print("\n❌ ERRO: Nenhuma zona carregada!")
            print("Arquivo zone_config.json existe mas está vazio ou corrompido")
            print("Execute: python quick_zone_setup.py")
            return

        for zone in self.zones:
            print(f"  - {zone['name']}: {len(zone['points'])} pontos")
            print(f"    Coords: {zone['points'][0]} -> {zone['points'][2]}")

        print("\nPressione 'q' para sair")
        print("Pressione 's' para salvar snapshot")
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
                processed_frame, dog_boxes, violation, should_alert = self.process_frame(
                    frame, current_time
                )

                # Draw zones
                processed_frame = self.draw_zones(processed_frame)

                # Draw detections
                processed_frame = self.draw_detections(processed_frame, dog_boxes, violation)

                # Draw info
                processed_frame = self.draw_info(processed_frame, violation, fps)

                # Active training alerts
                if self.enable_trainer and self.trainer:
                    if violation:
                        # Dog is in zone - alert to train
                        self.trainer.alert(self.frames_in_zone)
                        self.was_in_zone = True
                    else:
                        # Dog left zone - positive reinforcement
                        if self.was_in_zone and self.frames_in_zone > 30:
                            self.trainer.positive_reinforcement()
                        self.was_in_zone = False

                # Alert if needed (logging/notification)
                if should_alert and violation:
                    alert_info = {
                        'detection_type': 'zone_violation',
                        'zone_name': violation['zone']['name'],
                        'confidence': 1.0,
                        'frames_detected': self.frames_in_zone
                    }
                    self.notifier.notify(processed_frame, alert_info)

                # Display
                cv2.imshow('Zone Detector', processed_frame)

                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"data/snapshot_{timestamp}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    self.logger.info(f"Snapshot saved: {filename}")

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
    import argparse

    parser = argparse.ArgumentParser(description='DontPiss Zone Detector with Training')
    parser.add_argument('--mode', choices=['gentle', 'standard', 'intensive', 'silent'],
                       default='standard',
                       help='Training mode: gentle (soft alerts), standard (normal), intensive (strong), silent (no trainer)')
    parser.add_argument('--no-trainer', action='store_true',
                       help='Disable active training alerts (only log violations)')

    args = parser.parse_args()

    try:
        # Silent mode = no trainer
        enable_trainer = not args.no_trainer and args.mode != 'silent'
        training_mode = args.mode if args.mode != 'silent' else 'standard'

        if enable_trainer:
            print(f"\n🎓 Training mode: {training_mode.upper()}")
            print("   Active training alerts enabled")
        else:
            print("\n📊 Silent mode: Only logging violations")

        detector = ZoneDetector(training_mode=training_mode, enable_trainer=enable_trainer)
        detector.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
