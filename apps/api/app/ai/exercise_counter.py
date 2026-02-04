"""
运动计数器 - 基于姿态分析
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from app.ai.pose_analyzer import PoseAnalyzer, PoseLandmarks


class ExerciseState(str, Enum):
    """运动状态"""
    IDLE = "idle"
    UP = "up"
    DOWN = "down"
    HOLD = "hold"


@dataclass
class ExerciseResult:
    """运动分析结果"""
    count: int
    state: str
    feedback: str
    is_correct: bool
    accuracy: float = 100.0


class BaseExercise(ABC):
    """运动基类"""

    def __init__(self):
        self.analyzer = PoseAnalyzer()
        self.count = 0
        self.state = ExerciseState.IDLE
        self.correct_reps = 0
        self.total_reps = 0

    @abstractmethod
    def analyze(self, landmarks: PoseLandmarks) -> ExerciseResult:
        """分析动作"""
        pass

    def reset(self):
        """重置计数"""
        self.count = 0
        self.state = ExerciseState.IDLE
        self.correct_reps = 0
        self.total_reps = 0

    def get_accuracy(self) -> float:
        """获取准确率"""
        if self.total_reps == 0:
            return 100.0
        return (self.correct_reps / self.total_reps) * 100


class SquatExercise(BaseExercise):
    """深蹲运动"""

    SQUAT_THRESHOLD = 100  # 深蹲角度阈值
    STAND_THRESHOLD = 160  # 站立角度阈值

    def analyze(self, landmarks: PoseLandmarks) -> ExerciseResult:
        left_knee = self.analyzer.get_knee_angle(landmarks, "left")
        right_knee = self.analyzer.get_knee_angle(landmarks, "right")
        avg_knee = (left_knee + right_knee) / 2

        feedback = ""
        is_correct = True

        # 状态机逻辑
        if self.state in [ExerciseState.IDLE, ExerciseState.UP]:
            if avg_knee < self.SQUAT_THRESHOLD:
                self.state = ExerciseState.DOWN
                # 检查动作质量
                if abs(left_knee - right_knee) > 20:
                    feedback = "注意保持双腿对称"
                    is_correct = False
                else:
                    feedback = "下蹲到位，保持住"

        elif self.state == ExerciseState.DOWN:
            if avg_knee > self.STAND_THRESHOLD:
                self.state = ExerciseState.UP
                self.count += 1
                self.total_reps += 1
                if is_correct:
                    self.correct_reps += 1
                feedback = f"完成第{self.count}个！"

        # 实时反馈
        if self.state == ExerciseState.UP and avg_knee > 140:
            feedback = feedback or "准备下蹲"
        elif self.state == ExerciseState.DOWN and avg_knee > self.SQUAT_THRESHOLD:
            feedback = feedback or "再蹲低一点"

        return ExerciseResult(
            count=self.count,
            state=self.state.value,
            feedback=feedback,
            is_correct=is_correct,
            accuracy=self.get_accuracy()
        )


class JumpingJackExercise(BaseExercise):
    """开合跳运动"""

    def __init__(self):
        super().__init__()
        self.prev_feet_distance = 0

    def analyze(self, landmarks: PoseLandmarks) -> ExerciseResult:
        feet_distance = self.analyzer.get_feet_distance(landmarks)
        shoulder_width = self.analyzer.get_shoulder_width(landmarks)

        # 归一化脚间距
        normalized_distance = feet_distance / (shoulder_width + 1e-6)

        feedback = ""
        is_correct = True

        # 开合状态判断
        if self.state in [ExerciseState.IDLE, ExerciseState.DOWN]:
            if normalized_distance > 1.5:  # 脚打开
                self.state = ExerciseState.UP
                feedback = "手臂举高"

        elif self.state == ExerciseState.UP:
            if normalized_distance < 0.5:  # 脚合拢
                self.state = ExerciseState.DOWN
                self.count += 1
                self.total_reps += 1
                self.correct_reps += 1
                feedback = f"完成第{self.count}个！"

        self.prev_feet_distance = feet_distance

        return ExerciseResult(
            count=self.count,
            state=self.state.value,
            feedback=feedback,
            is_correct=is_correct,
            accuracy=self.get_accuracy()
        )


class HighKneesExercise(BaseExercise):
    """高抬腿运动"""

    def __init__(self):
        super().__init__()
        self.last_leg = None  # 上一次抬起的腿

    def analyze(self, landmarks: PoseLandmarks) -> ExerciseResult:
        left_hip = landmarks.get(PoseAnalyzer.LEFT_HIP)
        right_hip = landmarks.get(PoseAnalyzer.RIGHT_HIP)
        left_knee = landmarks.get(PoseAnalyzer.LEFT_KNEE)
        right_knee = landmarks.get(PoseAnalyzer.RIGHT_KNEE)

        hip_y = (left_hip.y + right_hip.y) / 2

        feedback = ""
        is_correct = True

        # 检测左腿抬起
        if left_knee.y < hip_y and self.last_leg != "left":
            self.count += 1
            self.last_leg = "left"
            self.total_reps += 1
            self.correct_reps += 1
            feedback = f"左腿！第{self.count}个"

        # 检测右腿抬起
        elif right_knee.y < hip_y and self.last_leg != "right":
            self.count += 1
            self.last_leg = "right"
            self.total_reps += 1
            self.correct_reps += 1
            feedback = f"右腿！第{self.count}个"

        if not feedback:
            feedback = "抬高膝盖，超过髋部"

        return ExerciseResult(
            count=self.count,
            state=self.state.value,
            feedback=feedback,
            is_correct=is_correct,
            accuracy=self.get_accuracy()
        )


class PushupExercise(BaseExercise):
    """俯卧撑运动"""

    DOWN_THRESHOLD = 90  # 下压角度阈值
    UP_THRESHOLD = 160  # 撑起角度阈值

    def analyze(self, landmarks: PoseLandmarks) -> ExerciseResult:
        left_elbow = self.analyzer.get_elbow_angle(landmarks, "left")
        right_elbow = self.analyzer.get_elbow_angle(landmarks, "right")
        avg_elbow = (left_elbow + right_elbow) / 2

        feedback = ""
        is_correct = True

        if self.state in [ExerciseState.IDLE, ExerciseState.UP]:
            if avg_elbow < self.DOWN_THRESHOLD:
                self.state = ExerciseState.DOWN
                feedback = "下压到位"

        elif self.state == ExerciseState.DOWN:
            if avg_elbow > self.UP_THRESHOLD:
                self.state = ExerciseState.UP
                self.count += 1
                self.total_reps += 1
                self.correct_reps += 1
                feedback = f"完成第{self.count}个！"

        if not feedback:
            if self.state == ExerciseState.UP:
                feedback = "准备下压"
            else:
                feedback = "撑起身体"

        return ExerciseResult(
            count=self.count,
            state=self.state.value,
            feedback=feedback,
            is_correct=is_correct,
            accuracy=self.get_accuracy()
        )


class LungeExercise(BaseExercise):
    """弓步蹲运动"""

    LUNGE_THRESHOLD = 100
    STAND_THRESHOLD = 160

    def __init__(self):
        super().__init__()
        self.last_leg = None

    def analyze(self, landmarks: PoseLandmarks) -> ExerciseResult:
        left_knee = self.analyzer.get_knee_angle(landmarks, "left")
        right_knee = self.analyzer.get_knee_angle(landmarks, "right")

        feedback = ""
        is_correct = True

        # 检测左腿弓步
        if left_knee < self.LUNGE_THRESHOLD and right_knee > self.STAND_THRESHOLD:
            if self.last_leg != "left":
                self.state = ExerciseState.DOWN
                self.last_leg = "left"

        # 检测右腿弓步
        elif right_knee < self.LUNGE_THRESHOLD and left_knee > self.STAND_THRESHOLD:
            if self.last_leg != "right":
                self.state = ExerciseState.DOWN
                self.last_leg = "right"

        # 检测站立恢复
        elif left_knee > self.STAND_THRESHOLD and right_knee > self.STAND_THRESHOLD:
            if self.state == ExerciseState.DOWN:
                self.count += 1
                self.total_reps += 1
                self.correct_reps += 1
                feedback = f"完成第{self.count}个！"
            self.state = ExerciseState.UP

        if not feedback:
            feedback = "交替弓步蹲"

        return ExerciseResult(
            count=self.count,
            state=self.state.value,
            feedback=feedback,
            is_correct=is_correct,
            accuracy=self.get_accuracy()
        )


class ExerciseCounter:
    """运动计数器工厂"""

    EXERCISES = {
        "squat": SquatExercise,
        "jumping_jack": JumpingJackExercise,
        "high_knees": HighKneesExercise,
        "pushup": PushupExercise,
        "lunge": LungeExercise,
    }

    @classmethod
    def create(cls, exercise_type: str) -> BaseExercise:
        """创建运动计数器"""
        exercise_class = cls.EXERCISES.get(exercise_type)
        if not exercise_class:
            raise ValueError(f"不支持的运动类型: {exercise_type}")
        return exercise_class()

    @classmethod
    def list_exercises(cls) -> List[str]:
        """列出支持的运动类型"""
        return list(cls.EXERCISES.keys())
