"""
Pose Analyzer module for detecting dog urination behavior
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PoseAnalyzer:
    """Analyzes dog pose to detect urination behavior"""

    def __init__(self, config):
        self.config = config
        self.pee_config = config.PEE_DETECTION
        self.keypoint_indices = config.KEYPOINT_INDICES
        self.detection_counter = 0
        self.last_detection_time = 0

    def calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        Calculate angle between three points
        Args:
            p1, p2, p3: Points as [x, y] arrays, where p2 is the vertex
        Returns:
            Angle in degrees
        """
        v1 = p1 - p2
        v2 = p3 - p2

        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        return np.degrees(angle)

    def calculate_distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        """Calculate Euclidean distance between two points"""
        return np.linalg.norm(p1 - p2)

    def detect_leg_lift(self, keypoints: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if dog is lifting leg (typical male urination pose)
        Args:
            keypoints: Array of shape (N, 3) where N is number of keypoints,
                      columns are [x, y, confidence]
        Returns:
            Tuple of (is_lifting_leg, confidence_score)
        """
        try:
            # Extract relevant keypoints
            left_hip = keypoints[self.keypoint_indices['left_hip']][:2]
            left_knee = keypoints[self.keypoint_indices['left_knee']][:2]
            left_paw = keypoints[self.keypoint_indices['left_back_paw']][:2]

            right_hip = keypoints[self.keypoint_indices['right_hip']][:2]
            right_knee = keypoints[self.keypoint_indices['right_knee']][:2]
            right_paw = keypoints[self.keypoint_indices['right_back_paw']][:2]

            # Check left leg
            left_angle = self.calculate_angle(left_hip, left_knee, left_paw)
            left_height = abs(left_paw[1] - left_hip[1])

            # Check right leg
            right_angle = self.calculate_angle(right_hip, right_knee, right_paw)
            right_height = abs(right_paw[1] - right_hip[1])

            # Body height reference
            shoulder = keypoints[self.keypoint_indices['left_shoulder']][:2]
            hip = keypoints[self.keypoint_indices['left_hip']][:2]
            body_height = self.calculate_distance(shoulder, hip)

            # Detect if one leg is significantly raised
            threshold_angle = self.pee_config['leg_lift_angle_threshold']
            height_ratio = self.pee_config['leg_lift_height_ratio']

            left_lifted = (left_angle < threshold_angle and
                          left_height > body_height * height_ratio)
            right_lifted = (right_angle < threshold_angle and
                           right_height > body_height * height_ratio)

            is_lifting = left_lifted or right_lifted
            confidence = max(
                min(left_angle / threshold_angle, 1.0) if left_lifted else 0,
                min(right_angle / threshold_angle, 1.0) if right_lifted else 0
            )

            return is_lifting, confidence

        except Exception as e:
            logger.debug(f"Error in leg lift detection: {e}")
            return False, 0.0

    def detect_squat(self, keypoints: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if dog is squatting (typical female urination pose)
        Args:
            keypoints: Array of keypoints
        Returns:
            Tuple of (is_squatting, confidence_score)
        """
        try:
            # Get body reference points
            shoulder = keypoints[self.keypoint_indices['left_shoulder']][:2]
            hip = keypoints[self.keypoint_indices['left_hip']][:2]
            knee = keypoints[self.keypoint_indices['left_knee']][:2]
            paw = keypoints[self.keypoint_indices['left_back_paw']][:2]

            # Calculate body lowering
            body_height = self.calculate_distance(shoulder, hip)
            leg_height = self.calculate_distance(hip, paw)
            height_ratio = leg_height / (body_height + 1e-6)

            # Calculate leg spread
            left_paw = keypoints[self.keypoint_indices['left_back_paw']][:2]
            right_paw = keypoints[self.keypoint_indices['right_back_paw']][:2]
            paw_distance = self.calculate_distance(left_paw, right_paw)
            width_ratio = paw_distance / (body_height + 1e-6)

            # Check squat conditions
            is_lowered = height_ratio < self.pee_config['squat_height_ratio']
            is_wide = width_ratio > self.pee_config['squat_width_ratio']

            is_squatting = is_lowered and is_wide
            confidence = (1 - height_ratio) * 0.6 + (width_ratio - 1) * 0.4

            return is_squatting, max(0, min(confidence, 1.0))

        except Exception as e:
            logger.debug(f"Error in squat detection: {e}")
            return False, 0.0

    def check_tail_position(self, keypoints: np.ndarray) -> bool:
        """Check if tail is in raised position (common during urination)"""
        try:
            tail_base = keypoints[self.keypoint_indices['tail_base']][:2]
            tail_end = keypoints[self.keypoint_indices['tail_end']][:2]
            hip = keypoints[self.keypoint_indices['left_hip']][:2]

            # Tail is raised if tail_end is above or level with tail_base
            is_raised = tail_end[1] <= tail_base[1]
            return is_raised
        except:
            return False

    def analyze_pose(self, keypoints: np.ndarray, current_time: float) -> Dict:
        """
        Main analysis function to detect urination behavior
        Args:
            keypoints: Detected keypoints from pose estimation
            current_time: Current timestamp
        Returns:
            Dictionary with detection results
        """
        result = {
            'is_peeing': False,
            'confidence': 0.0,
            'detection_type': None,
            'frames_detected': 0,
            # Debug info
            'debug': {
                'leg_lift_detected': False,
                'leg_lift_confidence': 0.0,
                'squat_detected': False,
                'squat_confidence': 0.0,
                'tail_raised': False,
                'detection_counter': 0,
                'min_frames_needed': self.pee_config['min_frames_threshold']
            }
        }

        if keypoints is None or len(keypoints) == 0:
            self.detection_counter = 0
            return result

        # Check for leg lift
        leg_lift, leg_confidence = self.detect_leg_lift(keypoints)

        # Check for squat
        squat, squat_confidence = self.detect_squat(keypoints)

        # Check tail position
        tail_raised = self.check_tail_position(keypoints)

        # Update debug info
        result['debug']['leg_lift_detected'] = leg_lift
        result['debug']['leg_lift_confidence'] = leg_confidence
        result['debug']['squat_detected'] = squat
        result['debug']['squat_confidence'] = squat_confidence
        result['debug']['tail_raised'] = tail_raised

        # Determine if peeing
        max_confidence = max(leg_confidence, squat_confidence)

        # Bonus confidence if tail is raised
        if tail_raised and (leg_lift or squat):
            max_confidence = min(max_confidence * 1.2, 1.0)

        if leg_lift or squat:
            self.detection_counter += 1
        else:
            self.detection_counter = 0

        result['debug']['detection_counter'] = self.detection_counter

        # Check if detection threshold is met
        min_frames = self.pee_config['min_frames_threshold']
        cooldown = self.pee_config['cooldown_seconds']

        if self.detection_counter >= min_frames:
            # Check cooldown period
            time_since_last = current_time - self.last_detection_time
            if time_since_last > cooldown:
                result['is_peeing'] = True
                result['confidence'] = max_confidence
                result['detection_type'] = 'leg_lift' if leg_lift else 'squat'
                result['frames_detected'] = self.detection_counter
                self.last_detection_time = current_time

        return result

    def reset_detection(self):
        """Reset detection counter"""
        self.detection_counter = 0
