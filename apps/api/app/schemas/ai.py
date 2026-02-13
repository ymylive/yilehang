"""AI-related schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JumpRopeAnalyzeRequest(BaseModel):
    """Jump rope analysis request."""

    student_id: int = Field(..., description="Student ID")
    video_url: Optional[str] = Field(None, description="Video URL (optional)")
    fps: Optional[int] = Field(30, description="Video FPS")
    duration_sec: Optional[int] = Field(None, description="Duration in seconds")
    meta: Optional[Dict[str, Any]] = Field(None, description="Client metadata")


class JumpRopeAnalyzeResponse(BaseModel):
    """Jump rope analysis response."""

    reps_count: int
    accuracy_score: float
    confidence: float
    issues: List[str]
    suggestions: List[str]
    model_version: str


class AiAdviceRequest(BaseModel):
    """AI training + diet advice request."""

    student_id: Optional[int] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None
    recent_sessions: Optional[List[Dict[str, Any]]] = None
    diet_preference: Optional[str] = None


class AiAdviceResponse(BaseModel):
    """AI advice response."""

    sport_advice: List[str]
    diet_advice: List[str]
    safety_tips: List[str]
    disclaimer: str


class AiChatRequest(BaseModel):
    """AI chat request."""

    question: str
    context: Optional[Dict[str, Any]] = None


class AiChatResponse(BaseModel):
    """AI chat response."""

    answer: str
    suggested_actions: List[str]
    disclaimer: str
