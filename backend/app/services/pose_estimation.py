"""
FITRON Pose Estimation Service
Real-time pose detection using OpenCV, YOLO, and MediaPipe
"""

import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
import torch
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class PoseLandmark(Enum):
    """MediaPipe pose landmarks"""
    NOSE = 0
    LEFT_EYE = 1
    RIGHT_EYE = 2
    LEFT_EAR = 3
    RIGHT_EAR = 4
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

@dataclass
class PoseData:
    """Pose data structure"""
    landmarks: Dict[int, Tuple[float, float, float]]  # landmark_id -> (x, y, z)
    angles: Dict[str, float]  # joint_name -> angle_degrees
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    pose_type: str  # "standing", "squat", "deadlift", etc.

@dataclass
class RepAnalysis:
    """Rep analysis result"""
    rep_count: int
    form_score: float
    rep_quality: str
    is_ego_lifting: bool
    velocity: float
    range_of_motion: float
    feedback: str
    suggestions: List[str]

class PoseEstimationService:
    """Pose estimation service for FITRON"""
    
    def __init__(self):
        """Initialize pose estimation models"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize YOLO model
        try:
            self.yolo_model = YOLO(settings.YOLO_MODEL_PATH)
            logger.info("✅ YOLO model loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ YOLO model not found, using MediaPipe only: {e}")
            self.yolo_model = None
        
        # Exercise-specific pose analyzers
        self.exercise_analyzers = {
            "squat": self._analyze_squat_pose,
            "deadlift": self._analyze_deadlift_pose,
            "bench_press": self._analyze_bench_press_pose,
            "overhead_press": self._analyze_overhead_press_pose,
            "pull_up": self._analyze_pull_up_pose,
            "push_up": self._analyze_push_up_pose
        }
    
    def detect_pose(self, frame: np.ndarray) -> Optional[PoseData]:
        """Detect pose in a single frame"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # MediaPipe pose detection
            results = self.pose.process(rgb_frame)
            
            if not results.pose_landmarks:
                return None
            
            # Extract landmarks
            landmarks = {}
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks[i] = (landmark.x, landmark.y, landmark.z)
            
            # Calculate joint angles
            angles = self._calculate_joint_angles(landmarks)
            
            # Get bounding box
            bounding_box = self._get_bounding_box(landmarks, frame.shape)
            
            # Determine pose type
            pose_type = self._classify_pose(landmarks, angles)
            
            # Calculate confidence
            confidence = self._calculate_confidence(landmarks)
            
            return PoseData(
                landmarks=landmarks,
                angles=angles,
                confidence=confidence,
                bounding_box=bounding_box,
                pose_type=pose_type
            )
            
        except Exception as e:
            logger.error(f"Pose detection error: {e}")
            return None
    
    def analyze_rep_sequence(self, frames: List[np.ndarray], exercise_type: str) -> RepAnalysis:
        """Analyze a sequence of frames for rep counting and form analysis"""
        try:
            pose_data_sequence = []
            
            # Detect pose in all frames
            for frame in frames:
                pose_data = self.detect_pose(frame)
                if pose_data:
                    pose_data_sequence.append(pose_data)
            
            if not pose_data_sequence:
                return RepAnalysis(
                    rep_count=0,
                    form_score=0.0,
                    rep_quality="unknown",
                    is_ego_lifting=False,
                    velocity=0.0,
                    range_of_motion=0.0,
                    feedback="No pose detected",
                    suggestions=["Ensure camera is positioned correctly"]
                )
            
            # Analyze exercise-specific form
            if exercise_type in self.exercise_analyzers:
                analysis = self.exercise_analyzers[exercise_type](pose_data_sequence)
            else:
                analysis = self._analyze_generic_pose(pose_data_sequence)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Rep sequence analysis error: {e}")
            return RepAnalysis(
                rep_count=0,
                form_score=0.0,
                rep_quality="error",
                is_ego_lifting=False,
                velocity=0.0,
                range_of_motion=0.0,
                feedback=f"Analysis error: {str(e)}",
                suggestions=["Try again with better lighting"]
            )
    
    def _calculate_joint_angles(self, landmarks: Dict[int, Tuple[float, float, float]]) -> Dict[str, float]:
        """Calculate joint angles from landmarks"""
        angles = {}
        
        try:
            # Knee angles
            if all(k in landmarks for k in [PoseLandmark.LEFT_HIP.value, PoseLandmark.LEFT_KNEE.value, PoseLandmark.LEFT_ANKLE.value]):
                angles["left_knee"] = self._calculate_angle(
                    landmarks[PoseLandmark.LEFT_HIP.value],
                    landmarks[PoseLandmark.LEFT_KNEE.value],
                    landmarks[PoseLandmark.LEFT_ANKLE.value]
                )
            
            if all(k in landmarks for k in [PoseLandmark.RIGHT_HIP.value, PoseLandmark.RIGHT_KNEE.value, PoseLandmark.RIGHT_ANKLE.value]):
                angles["right_knee"] = self._calculate_angle(
                    landmarks[PoseLandmark.RIGHT_HIP.value],
                    landmarks[PoseLandmark.RIGHT_KNEE.value],
                    landmarks[PoseLandmark.RIGHT_ANKLE.value]
                )
            
            # Hip angles
            if all(k in landmarks for k in [PoseLandmark.LEFT_SHOULDER.value, PoseLandmark.LEFT_HIP.value, PoseLandmark.LEFT_KNEE.value]):
                angles["left_hip"] = self._calculate_angle(
                    landmarks[PoseLandmark.LEFT_SHOULDER.value],
                    landmarks[PoseLandmark.LEFT_HIP.value],
                    landmarks[PoseLandmark.LEFT_KNEE.value]
                )
            
            # Shoulder angles
            if all(k in landmarks for k in [PoseLandmark.LEFT_ELBOW.value, PoseLandmark.LEFT_SHOULDER.value, PoseLandmark.LEFT_HIP.value]):
                angles["left_shoulder"] = self._calculate_angle(
                    landmarks[PoseLandmark.LEFT_ELBOW.value],
                    landmarks[PoseLandmark.LEFT_SHOULDER.value],
                    landmarks[PoseLandmark.LEFT_HIP.value]
                )
            
        except Exception as e:
            logger.error(f"Angle calculation error: {e}")
        
        return angles
    
    def _calculate_angle(self, point1: Tuple[float, float, float], 
                        point2: Tuple[float, float, float], 
                        point3: Tuple[float, float, float]) -> float:
        """Calculate angle between three points"""
        try:
            # Convert to numpy arrays
            a = np.array([point1[0], point1[1]])
            b = np.array([point2[0], point2[1]])
            c = np.array([point3[0], point3[1]])
            
            # Calculate vectors
            ba = a - b
            bc = c - b
            
            # Calculate angle
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except Exception as e:
            logger.error(f"Angle calculation error: {e}")
            return 0.0
    
    def _get_bounding_box(self, landmarks: Dict[int, Tuple[float, float, float]], 
                         frame_shape: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
        """Get bounding box from landmarks"""
        try:
            x_coords = [landmark[0] for landmark in landmarks.values()]
            y_coords = [landmark[1] for landmark in landmarks.values()]
            
            x_min = int(min(x_coords) * frame_shape[1])
            x_max = int(max(x_coords) * frame_shape[1])
            y_min = int(min(y_coords) * frame_shape[0])
            y_max = int(max(y_coords) * frame_shape[0])
            
            return (x_min, y_min, x_max - x_min, y_max - y_min)
        except Exception as e:
            logger.error(f"Bounding box calculation error: {e}")
            return (0, 0, 0, 0)
    
    def _classify_pose(self, landmarks: Dict[int, Tuple[float, float, float]], 
                      angles: Dict[str, float]) -> str:
        """Classify the type of pose"""
        try:
            # Simple pose classification based on knee angles
            if "left_knee" in angles and "right_knee" in angles:
                avg_knee_angle = (angles["left_knee"] + angles["right_knee"]) / 2
                
                if avg_knee_angle < 90:
                    return "squat"
                elif avg_knee_angle < 120:
                    return "partial_squat"
                else:
                    return "standing"
            
            return "unknown"
        except Exception as e:
            logger.error(f"Pose classification error: {e}")
            return "unknown"
    
    def _calculate_confidence(self, landmarks: Dict[int, Tuple[float, float, float]]) -> float:
        """Calculate confidence score for pose detection"""
        try:
            # Simple confidence based on number of detected landmarks
            total_landmarks = len(self.mp_pose.PoseLandmark)
            detected_landmarks = len(landmarks)
            
            return detected_landmarks / total_landmarks
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.0
    
    def _analyze_squat_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Analyze squat form"""
        # Implementation for squat analysis
        # This would include rep counting, form scoring, ego-lifting detection
        return self._analyze_generic_pose(pose_sequence)
    
    def _analyze_deadlift_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Analyze deadlift form"""
        return self._analyze_generic_pose(pose_sequence)
    
    def _analyze_bench_press_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Analyze bench press form"""
        return self._analyze_generic_pose(pose_sequence)
    
    def _analyze_overhead_press_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Analyze overhead press form"""
        return self._analyze_generic_pose(pose_sequence)
    
    def _analyze_pull_up_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Analyze pull-up form"""
        return self._analyze_generic_pose(pose_sequence)
    
    def _analyze_push_up_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Analyze push-up form"""
        return self._analyze_generic_pose(pose_sequence)
    
    def _analyze_generic_pose(self, pose_sequence: List[PoseData]) -> RepAnalysis:
        """Generic pose analysis"""
        if not pose_sequence:
            return RepAnalysis(
                rep_count=0,
                form_score=0.0,
                rep_quality="unknown",
                is_ego_lifting=False,
                velocity=0.0,
                range_of_motion=0.0,
                feedback="No pose data available",
                suggestions=["Ensure proper camera positioning"]
            )
        
        # Calculate average confidence
        avg_confidence = sum(pose.confidence for pose in pose_sequence) / len(pose_sequence)
        
        # Simple rep counting (placeholder)
        rep_count = len(pose_sequence) // 10  # Simplified logic
        
        # Form scoring based on confidence
        form_score = avg_confidence
        
        # Determine rep quality
        if form_score > 0.8:
            rep_quality = "excellent"
        elif form_score > 0.6:
            rep_quality = "good"
        elif form_score > 0.4:
            rep_quality = "fair"
        else:
            rep_quality = "poor"
        
        # Ego-lifting detection (placeholder)
        is_ego_lifting = False
        
        return RepAnalysis(
            rep_count=rep_count,
            form_score=form_score,
            rep_quality=rep_quality,
            is_ego_lifting=is_ego_lifting,
            velocity=0.0,  # Placeholder
            range_of_motion=0.0,  # Placeholder
            feedback=f"Form score: {form_score:.2f}",
            suggestions=["Keep practicing for better form"]
        )

# Global instance
pose_service = PoseEstimationService() 