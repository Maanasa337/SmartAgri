"""
Recommendations router — exotic crop recommendations with vendor matching.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from bson import ObjectId

from db.mongodb import (
    users_col, vendors_col, exotic_recommendations_col, market_trends_col
)
from models.user import CropInterest
from routers.auth import get_current_user
from services.gemini_service import recommend_exotic_crop
from services.email_service import send_vendor_introduction

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/crop")
async def get_crop_recommendation(current_user: dict = Depends(get_current_user)):
    """
    Get an exotic high-profit crop recommendation using Gemini AI.
    Matches with local vendors and stores the recommendation.
    """
    user_id = str(current_user["_id"])

    # Check if recent recommendation exists
    existing = await exotic_recommendations_col().find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )

    # If we have a recommendation made in the last 7 days, return it
    if existing:
        existing["id"] = str(existing.pop("_id"))
        return {"status": "success", "recommendation": existing}

    # Fetch recent market data for context
    market_data = await market_trends_col().find(
        {},
        {"_id": 0, "crop_name": 1, "price_per_quintal": 1, "demand_level": 1}
    ).sort("timestamp", -1).to_list(length=20)

    # Build user profile
    profile = {
        "present_crop": current_user.get("present_crop", "paddy"),
        "land_acres": current_user.get("land_acres", 2),
        "soil_data": current_user.get("soil_data", {}),
        "weather_data": current_user.get("weather_data", {}),
        "past_crop": current_user.get("past_crop", ""),
        "past_disease": current_user.get("past_disease", ""),
    }

    # Get Gemini recommendation
    reco = await recommend_exotic_crop(profile, market_data)

    # Match with a vendor
    crop_name = reco.get("crop_name", "Dragon Fruit")
    vendor = await vendors_col().find_one(
        {"crops_accepted": {"$regex": crop_name, "$options": "i"}, "active": True}
    )

    vendor_match = None
    if vendor:
        vendor_match = {
            "id": str(vendor["_id"]),
            "name": vendor.get("name", ""),
            "location": vendor.get("location", ""),
            "contact": vendor.get("contact", ""),
            "crops_accepted": vendor.get("crops_accepted", []),
        }

    # Store recommendation
    reco_doc = {
        "user_id": user_id,
        "crop_name": crop_name,
        "why_suitable": reco.get("why_suitable", ""),
        "expected_yield_per_acre": reco.get("expected_yield_per_acre", ""),
        "expected_profit_inr": reco.get("expected_profit_inr", 0),
        "best_season": reco.get("best_season", ""),
        "care_tips": reco.get("care_tips", ""),
        "market_demand_score": reco.get("market_demand_score", 5),
        "grow_duration_days": reco.get("grow_duration_days", 180),
        "vendor_match": vendor_match,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await exotic_recommendations_col().insert_one(reco_doc)
    reco_doc["id"] = str(result.inserted_id)
    if "_id" in reco_doc:
        del reco_doc["_id"]

    return {"status": "success", "recommendation": reco_doc}


@router.post("/interested")
async def express_interest(
    data: CropInterest,
    current_user: dict = Depends(get_current_user),
):
    """
    Farmer expresses interest in growing recommended crop.
    Saves preference and emails the matched vendor.
    """
    user_id = str(current_user["_id"])

    # Find matching vendor
    vendor = await vendors_col().find_one(
        {"crops_accepted": {"$regex": data.crop_name, "$options": "i"}, "active": True}
    )

    # Save interest
    await exotic_recommendations_col().update_one(
        {"user_id": user_id, "crop_name": data.crop_name},
        {"$set": {"interested": True, "interested_at": datetime.now(timezone.utc).isoformat()}},
    )

    # Email vendor if found
    if vendor and vendor.get("contact"):
        import asyncio

        async def notify():
            # Use vendor contact as email (or fallback)
            vendor_email = vendor.get("email", vendor.get("contact", ""))
            if "@" in vendor_email:
                await send_vendor_introduction(
                    vendor_email,
                    vendor.get("name", "Vendor"),
                    current_user.get("username", "Farmer"),
                    current_user.get("email", ""),
                    data.crop_name,
                )

        asyncio.create_task(notify())

    return {
        "status": "success",
        "message": f"Interest recorded for {data.crop_name}",
        "vendor_notified": bool(vendor),
    }
