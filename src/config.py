"""
Configuration file for Dog Pee Detection System
"""

# Camera settings
CAMERA_INDEX = 0  # 0 for webcam padrão, 1 para câmera externa, ou "/caminho/video.mp4" para arquivo
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS = 30

# Model settings
MODEL_TYPE = "yolo"  # Options: "yolo", "superanimal"
YOLO_MODEL = "yolov8n-pose.pt"  # Nano model for speed
CONFIDENCE_THRESHOLD = 0.5

# Pose detection settings
# Keypoint indices for dog pose (YOLO format)
# Typical dog keypoints: nose, eyes, ears, shoulders, elbows, paws, hips, knees, tail
KEYPOINT_INDICES = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_front_paw': 9,
    'right_front_paw': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_back_paw': 15,
    'right_back_paw': 16,
    'tail_base': 17,
    'tail_end': 18
}

# Pee detection heuristics
PEE_DETECTION = {
    # Leg lift detection (male dogs)
    'leg_lift_angle_threshold': 40,  # degrees (more strict)
    'leg_lift_height_ratio': 0.35,  # leg height relative to body (more strict)

    # Squat detection (female dogs or male puppies)
    'squat_height_ratio': 0.45,  # body lowered by this ratio (more strict)
    'squat_width_ratio': 1.3,  # legs spread wider (more strict)

    # Tail position
    'tail_raised': True,  # tail typically raised during urination

    # Time threshold - must maintain pose for N frames
    'min_frames_threshold': 25,  # ~0.8 seconds at 30fps (reduced false positives)

    # Cooldown period (avoid duplicate alerts)
    'cooldown_seconds': 90,  # 1.5 minutes between alerts

    # Ignore detection if humans are nearby (optional)
    'ignore_with_humans_nearby': True,
    'human_proximity_threshold': 0.3  # 30% of frame width
}

# Notification settings
NOTIFICATIONS = {
    'enabled': True,
    'sound': True,
    'desktop_notification': True,
    'save_snapshot': True,
    'snapshot_dir': 'data/snapshots'
}

# Video recording
RECORDING = {
    'enabled': False,
    'duration_seconds': 10,  # record N seconds after detection
    'output_dir': 'data/recordings'
}

# Logging
LOG_FILE = 'logs/dog_pee_detector.log'
LOG_LEVEL = 'INFO'

# Display settings
DISPLAY = {
    'show_video': True,
    'show_keypoints': True,
    'show_skeleton': True,
    'show_detection_info': True,
    'debug_mode': True  # Show detailed detection metrics
}
