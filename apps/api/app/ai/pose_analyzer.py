"""
姿态分析器 - 基于MediaPipe
"""
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

import numpy as np


@dataclass
class Point:
    """关键点坐标"""
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


@dataclass
class PoseLandmarks:
    """姿态关键点集合"""
    landmarks: List[Point]

    def get(self, index: int) -> Point:
        """获取指定索引的关键点"""
        if 0 <= index < len(self.landmarks):
            return self.landmarks[index]
        return Point(0, 0, 0, 0)


class PoseAnalyzer:
    """姿态分析器"""

    # MediaPipe关键点索引
    NOSE = 0
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

    @staticmethod
    def calculate_angle(p1: Point, p2: Point, p3: Point) -> float:
        """
        计算三点形成的角度
        p2是顶点
        """
        # 向量 p2->p1
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        # 向量 p2->p3
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])

        # 计算角度
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)

        return math.degrees(angle)

    @staticmethod
    def calculate_distance(p1: Point, p2: Point) -> float:
        """计算两点之间的距离"""
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def get_knee_angle(self, landmarks: PoseLandmarks, side: str = "left") -> float:
        """获取膝关节角度"""
        if side == "left":
            hip = landmarks.get(self.LEFT_HIP)
            knee = landmarks.get(self.LEFT_KNEE)
            ankle = landmarks.get(self.LEFT_ANKLE)
        else:
            hip = landmarks.get(self.RIGHT_HIP)
            knee = landmarks.get(self.RIGHT_KNEE)
            ankle = landmarks.get(self.RIGHT_ANKLE)

        return self.calculate_angle(hip, knee, ankle)

    def get_hip_angle(self, landmarks: PoseLandmarks, side: str = "left") -> float:
        """获取髋关节角度"""
        if side == "left":
            shoulder = landmarks.get(self.LEFT_SHOULDER)
            hip = landmarks.get(self.LEFT_HIP)
            knee = landmarks.get(self.LEFT_KNEE)
        else:
            shoulder = landmarks.get(self.RIGHT_SHOULDER)
            hip = landmarks.get(self.RIGHT_HIP)
            knee = landmarks.get(self.RIGHT_KNEE)

        return self.calculate_angle(shoulder, hip, knee)

    def get_elbow_angle(self, landmarks: PoseLandmarks, side: str = "left") -> float:
        """获取肘关节角度"""
        if side == "left":
            shoulder = landmarks.get(self.LEFT_SHOULDER)
            elbow = landmarks.get(self.LEFT_ELBOW)
            wrist = landmarks.get(self.LEFT_WRIST)
        else:
            shoulder = landmarks.get(self.RIGHT_SHOULDER)
            elbow = landmarks.get(self.RIGHT_ELBOW)
            wrist = landmarks.get(self.RIGHT_WRIST)

        return self.calculate_angle(shoulder, elbow, wrist)

    def get_shoulder_width(self, landmarks: PoseLandmarks) -> float:
        """获取肩宽"""
        left_shoulder = landmarks.get(self.LEFT_SHOULDER)
        right_shoulder = landmarks.get(self.RIGHT_SHOULDER)
        return self.calculate_distance(left_shoulder, right_shoulder)

    def get_feet_distance(self, landmarks: PoseLandmarks) -> float:
        """获取双脚间距"""
        left_ankle = landmarks.get(self.LEFT_ANKLE)
        right_ankle = landmarks.get(self.RIGHT_ANKLE)
        return self.calculate_distance(left_ankle, right_ankle)

    def is_standing(self, landmarks: PoseLandmarks) -> bool:
        """判断是否站立"""
        left_knee_angle = self.get_knee_angle(landmarks, "left")
        right_knee_angle = self.get_knee_angle(landmarks, "right")
        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
        return avg_knee_angle > 160

    def is_squatting(self, landmarks: PoseLandmarks) -> bool:
        """判断是否深蹲"""
        left_knee_angle = self.get_knee_angle(landmarks, "left")
        right_knee_angle = self.get_knee_angle(landmarks, "right")
        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
        return avg_knee_angle < 100

    def analyze_posture(self, landmarks: PoseLandmarks) -> Dict:
        """分析整体姿态"""
        return {
            "left_knee_angle": self.get_knee_angle(landmarks, "left"),
            "right_knee_angle": self.get_knee_angle(landmarks, "right"),
            "left_hip_angle": self.get_hip_angle(landmarks, "left"),
            "right_hip_angle": self.get_hip_angle(landmarks, "right"),
            "left_elbow_angle": self.get_elbow_angle(landmarks, "left"),
            "right_elbow_angle": self.get_elbow_angle(landmarks, "right"),
            "shoulder_width": self.get_shoulder_width(landmarks),
            "feet_distance": self.get_feet_distance(landmarks),
            "is_standing": self.is_standing(landmarks),
            "is_squatting": self.is_squatting(landmarks),
        }
