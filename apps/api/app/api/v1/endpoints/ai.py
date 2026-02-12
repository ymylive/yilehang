"""AI endpoints (stub)."""
from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas import (
    AiAdviceRequest,
    AiAdviceResponse,
    AiChatRequest,
    AiChatResponse,
    JumpRopeAnalyzeRequest,
    JumpRopeAnalyzeResponse,
)

router = APIRouter()


def _bmi_tip(height_cm: float, weight_kg: float):
    height_m = height_cm / 100.0
    if height_m <= 0:
        return None
    bmi = weight_kg / (height_m * height_m)
    if bmi < 18.5:
        return "Underweight: prioritize nutrition and sleep"
    if bmi < 24:
        return "Healthy range: keep consistent training habits"
    if bmi < 28:
        return "Overweight: increase low-impact cardio gradually"
    return "High BMI: build habits gradually and avoid overtraining"


@router.post(
    "/jump-rope/analyze",
    response_model=JumpRopeAnalyzeResponse,
    summary="Jump rope analysis",
)
async def jump_rope_analyze(
    data: JumpRopeAnalyzeRequest,
    current_user: dict = Depends(get_current_user),
):
    # Placeholder: integrate real CV model later
    return JumpRopeAnalyzeResponse(
        reps_count=0,
        accuracy_score=0.0,
        confidence=0.0,
        issues=["AI module not enabled", "Upload a clear 10-20s video"],
        suggestions=["Keep full body in frame", "Distance 2-3m", "Good lighting"],
        model_version="stub-0.1",
    )


@router.post("/advice", response_model=AiAdviceResponse, summary="Training & diet advice")
async def ai_advice(
    data: AiAdviceRequest,
    current_user: dict = Depends(get_current_user),
):
    sport_advice = [
        "Aim for 3-5 workouts per week, 20-40 minutes each",
        "Warm up and cool down to reduce injury risk",
        "Prioritize form before intensity",
    ]

    if data.recent_sessions and len(data.recent_sessions) < 3:
        sport_advice.append("Recent activity is low; start with short, frequent sessions")

    if data.height_cm and data.weight_kg:
        tip = _bmi_tip(data.height_cm, data.weight_kg)
        if tip:
            sport_advice.append(tip)

    diet_advice = [
        "Keep regular meals with protein and vegetables",
        "Hydrate after training; limit sugary drinks",
        "Avoid high-fat snacks close to bedtime",
    ]

    safety_tips = [
        "Stop training if you feel unwell",
        "Kids should train with supervision and gradual progression",
    ]

    return AiAdviceResponse(
        sport_advice=sport_advice,
        diet_advice=diet_advice,
        safety_tips=safety_tips,
        disclaimer="AI advice is for reference only; consult a coach for plans",
    )


@router.post("/chat", response_model=AiChatResponse, summary="AI Q&A")
async def ai_chat(
    data: AiChatRequest,
    current_user: dict = Depends(get_current_user),
):
    answer = (
        "I received your question. This AI module is in beta, "
        "please follow your coach's guidance as the primary source."
    )
    return AiChatResponse(
        answer=answer,
        suggested_actions=["View this week's training", "Book a coach review"],
        disclaimer="AI responses are informational only",
    )
