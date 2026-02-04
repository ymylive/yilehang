"""
成长档案相关Schema
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


class FitnessMetricBase(BaseModel):
    """体测指标基础Schema"""
    metric_type: str
    metric_name: str
    value: float
    score: Optional[float] = None
    national_percentile: Optional[float] = None


class FitnessMetricCreate(FitnessMetricBase):
    """体测指标创建Schema"""
    pass


class FitnessMetricResponse(FitnessMetricBase):
    """体测指标响应Schema"""
    id: int

    class Config:
        from_attributes = True


class FitnessTestBase(BaseModel):
    """体测记录基础Schema"""
    test_date: date
    height: Optional[float] = None
    weight: Optional[float] = None
    notes: Optional[str] = None


class FitnessTestCreate(FitnessTestBase):
    """体测记录创建Schema"""
    student_id: int
    tester_id: Optional[int] = None
    metrics: List[FitnessMetricCreate] = []


class FitnessTestResponse(FitnessTestBase):
    """体测记录响应Schema"""
    id: int
    student_id: int
    bmi: Optional[float] = None
    metrics: List[FitnessMetricResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class RadarChartData(BaseModel):
    """雷达图数据"""
    speed: float = 0
    agility: float = 0
    endurance: float = 0
    strength: float = 0
    flexibility: float = 0


class GrowthProfile(BaseModel):
    """成长档案"""
    student_id: int
    student_name: str
    current_radar: RadarChartData
    previous_radar: Optional[RadarChartData] = None
    total_training_hours: float = 0
    total_training_sessions: int = 0
    fitness_tests_count: int = 0


class TrainingSessionBase(BaseModel):
    """训练记录基础Schema"""
    exercise_type: str
    duration: int
    reps_count: int = 0
    accuracy_score: Optional[float] = None
    calories_burned: Optional[float] = None


class TrainingSessionCreate(TrainingSessionBase):
    """训练记录创建Schema"""
    student_id: int
    video_url: Optional[str] = None


class TrainingSessionResponse(TrainingSessionBase):
    """训练记录响应Schema"""
    id: int
    student_id: int
    video_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
