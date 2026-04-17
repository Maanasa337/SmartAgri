"""
Advisory router — generate weekly plans and voice chat with farm advisory agent.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from db.mongodb import users_col, advisory_plans_col
from models.user import AdvisoryPlanRequest, VoiceChatRequest
from routers.auth import get_current_user
from services.gemini_service import generate_advisory_plan
from services.voice_service import transcribe_audio, ask_advisory, text_to_speech

router = APIRouter(prefix="/api/advisory", tags=["advisory"])


@router.post("/generate-plan")
async def generate_plan(
    req: AdvisoryPlanRequest = AdvisoryPlanRequest(),
    current_user: dict = Depends(get_current_user),
):
    """Generate a weekly advisory plan using Gemini AI."""
    user_id = str(current_user["_id"])

    # Build profile for Gemini
    profile = {
        "present_crop": current_user.get("present_crop", "paddy"),
        "present_crop_stage": current_user.get("present_crop_stage", "vegetative"),
        "land_acres": current_user.get("land_acres", 2),
        "gps_coordinates": current_user.get("gps_coordinates", {}),
        "past_crop": current_user.get("past_crop", ""),
        "past_disease": current_user.get("past_disease", ""),
        "soil_data": current_user.get("soil_data", {}),
        "weather_data": current_user.get("weather_data", {}),
        "include_sustainable": req.include_sustainable,
    }

    # Generate plan via Gemini
    plan = await generate_advisory_plan(profile)

    # Get current week start (Monday)
    today = datetime.now(timezone.utc)
    week_start = today - __import__("datetime").timedelta(days=today.weekday())

    # Store in advisory_plans collection
    plan_doc = {
        "user_id": user_id,
        "week_start": week_start.strftime("%Y-%m-%d"),
        "irrigation_schedule": plan.get("irrigation_schedule", []),
        "pest_warnings": plan.get("pest_warnings", []),
        "harvest_plan": plan.get("harvest_plan", {}),
        "sustainable_tips": plan.get("sustainable_tips", []),
        "created_at": today.isoformat(),
    }

    # Upsert — replace existing plan for same week
    await advisory_plans_col().update_one(
        {"user_id": user_id, "week_start": plan_doc["week_start"]},
        {"$set": plan_doc},
        upsert=True,
    )

    # Schedule irrigation email reminders via background task
    import asyncio
    from services.email_service import send_irrigation_reminder

    async def schedule_reminders():
        try:
            email = current_user.get("email", "")
            crop = current_user.get("present_crop", "crop")
            for slot in plan.get("irrigation_schedule", []):
                await send_irrigation_reminder(email, crop, slot)
        except Exception as e:
            print(f"⚠ Email reminder scheduling error: {e}")

    asyncio.create_task(schedule_reminders())

    return {
        "status": "success",
        "plan": plan,
        "week_start": plan_doc["week_start"],
    }


@router.get("/current-plan")
async def get_current_plan(current_user: dict = Depends(get_current_user)):
    """Get the current week's advisory plan."""
    user_id = str(current_user["_id"])

    today = datetime.now(timezone.utc)
    week_start = today - __import__("datetime").timedelta(days=today.weekday())
    week_start_str = week_start.strftime("%Y-%m-%d")

    plan = await advisory_plans_col().find_one(
        {"user_id": user_id, "week_start": week_start_str},
        {"_id": 0},
    )

    if not plan:
        return {"status": "no_plan", "plan": None}

    return {"status": "success", "plan": plan}


@router.post("/voice-chat")
async def voice_chat(
    req: VoiceChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Handle voice chat with the farm advisory agent.
    Pipeline: audio → transcribe → ask AI → TTS response
    """
    # Step 1: Transcribe audio using farm_advisory model
    transcription = await transcribe_audio(req.audio_base64, req.lang_code)

    if transcription.get("error"):
        raise HTTPException(status_code=500, detail=f"Transcription failed: {transcription['error']}")

    user_question = transcription.get("translated", transcription.get("transcribed", ""))

    if not user_question:
        return {
            "transcribed": "",
            "translated": "",
            "answer": "I couldn't hear you clearly. Please try again.",
            "audio": "",
        }

    # Step 2: Build context-aware profile for advisory
    profile = {
        "name": current_user.get("username", "Farmer"),
        "current_crop": current_user.get("present_crop", ""),
        "crop_stage": current_user.get("present_crop_stage", ""),
        "total_area": str(current_user.get("land_acres", "")),
        "soil_type": current_user.get("soil_data", {}).get("texture", ""),
        "soil_ph": str(current_user.get("soil_data", {}).get("ph", "")),
        "state": "Tamil Nadu",
    }

    # Step 3: Ask farm advisory AI
    advisory_result = await ask_advisory(user_question, profile, is_comprehensive=False)
    answer = advisory_result.get("answer", "Sorry, I couldn't process that.")

    # Step 4: Convert answer to speech via TTS
    tts_result = await text_to_speech(answer, req.lang_code)

    return {
        "transcribed": transcription.get("transcribed", ""),
        "translated": user_question,
        "answer": answer,
        "translated_answer": tts_result.get("translated", answer),
        "audio": tts_result.get("audio", ""),
    }
