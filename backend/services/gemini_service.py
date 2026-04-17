"""
Gemini API integration for advisory plan generation and crop recommendations.
"""
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


async def generate_advisory_plan(user_profile: dict) -> dict:
    """
    Use Gemini to generate a structured weekly advisory plan.
    Returns JSON with irrigation_schedule, pest_warnings, harvest_plan, sustainable_tips.
    """
    prompt = f"""You are Krishi, an expert agricultural advisor for Tamil Nadu farmers.
Generate a detailed WEEKLY farm advisory plan for this farmer:

FARMER PROFILE:
- Crop: {user_profile.get('present_crop', 'paddy')}
- Crop Stage: {user_profile.get('present_crop_stage', 'vegetative')}
- Land: {user_profile.get('land_acres', 2)} acres
- Location GPS: {user_profile.get('gps_coordinates', {})}
- Past Crop: {user_profile.get('past_crop', '')}
- Past Disease: {user_profile.get('past_disease', '')}
- Soil Data: {json.dumps(user_profile.get('soil_data', {}))}
- Weather: {json.dumps(user_profile.get('weather_data', {}))}

Return ONLY valid JSON (no markdown, no backticks) with this exact structure:
{{
  "irrigation_schedule": [
    {{"day": "Monday", "time": "06:00", "duration_mins": 30, "method": "Drip"}},
    {{"day": "Wednesday", "time": "06:00", "duration_mins": 30, "method": "Drip"}},
    {{"day": "Friday", "time": "06:00", "duration_mins": 25, "method": "Drip"}},
    {{"day": "Sunday", "time": "06:30", "duration_mins": 30, "method": "Drip"}}
  ],
  "pest_warnings": [
    {{"pest": "Brown planthopper", "probability": 0.35, "preventive_action": "Apply neem oil spray 5ml/L"}}
  ],
  "harvest_plan": {{
    "expected_date": "2026-06-15",
    "yield_estimate": "22 quintals per acre",
    "post_harvest_tips": ["Dry grains to 14% moisture", "Store in jute bags"]
  }},
  "sustainable_tips": [
    "Use green manure with dhaincha between crop rows",
    "Apply vermicompost 2 tonnes/acre for improved soil health"
  ]
}}

Be specific to the crop, stage, soil conditions, and local Tamil Nadu weather patterns.
Include at least 4 irrigation slots, 2 pest warnings, and 3 sustainable tips.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        plan = json.loads(text)

        # Validate required keys
        required = ["irrigation_schedule", "pest_warnings", "harvest_plan", "sustainable_tips"]
        for key in required:
            if key not in plan:
                plan[key] = []

        return plan

    except Exception as e:
        print(f"⚠ Gemini advisory generation error: {e}")
        # Return a sensible fallback plan
        return {
            "irrigation_schedule": [
                {"day": "Monday", "time": "06:00", "duration_mins": 30, "method": "Flood"},
                {"day": "Wednesday", "time": "06:00", "duration_mins": 30, "method": "Flood"},
                {"day": "Friday", "time": "06:00", "duration_mins": 25, "method": "Flood"},
                {"day": "Sunday", "time": "06:30", "duration_mins": 30, "method": "Flood"},
            ],
            "pest_warnings": [
                {"pest": "Stem borer", "probability": 0.3, "preventive_action": "Install pheromone traps at 5/acre"},
                {"pest": "Leaf folder", "probability": 0.25, "preventive_action": "Spray Chlorantraniliprole 0.4ml/L"},
            ],
            "harvest_plan": {
                "expected_date": "2026-06-15",
                "yield_estimate": "20 quintals per acre",
                "post_harvest_tips": ["Sun dry to 14% moisture", "Store in clean jute bags", "Avoid storing with other grains"],
            },
            "sustainable_tips": [
                "Apply neem cake 250 kg/ha as organic pest deterrent",
                "Use Azolla as biofertilizer in paddy fields",
                "Practice crop rotation with pulses next season",
            ],
        }


async def recommend_exotic_crop(user_profile: dict, market_data: list) -> dict:
    """
    Use Gemini to recommend one exotic profitable crop.
    Returns structured recommendation with vendor match fields.
    """
    prompt = f"""You are an agricultural market analyst specializing in exotic high-value crops for Tamil Nadu, India.

FARMER PROFILE:
- Current Crop: {user_profile.get('present_crop', 'paddy')}
- Land: {user_profile.get('land_acres', 2)} acres
- Soil: {json.dumps(user_profile.get('soil_data', {}))}
- Weather: {json.dumps(user_profile.get('weather_data', {}))}
- Past Crop: {user_profile.get('past_crop', '')}
- Past Disease: {user_profile.get('past_disease', '')}

CURRENT MARKET TRENDS (recent prices):
{json.dumps(market_data[:5] if market_data else [])}

Recommend ONE exotic, high-profit crop from: dragon fruit, moringa, marigold (saffron substitute), quinoa, passion fruit.

Return ONLY valid JSON (no markdown, no backticks):
{{
  "crop_name": "Dragon Fruit",
  "why_suitable": "Well-suited to semi-arid Tamil Nadu climate with pH 6-7 soil",
  "expected_yield_per_acre": "6 tonnes",
  "expected_profit_inr": 250000,
  "best_season": "Year-round (main harvest June-November)",
  "care_tips": "Requires trellis support, moderate watering, full sun exposure",
  "market_demand_score": 8,
  "grow_duration_days": 365
}}
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)

    except Exception as e:
        print(f"⚠ Gemini recommendation error: {e}")
        return {
            "crop_name": "Dragon Fruit",
            "why_suitable": "Thrives in Tamil Nadu's warm climate, requires minimal water, high market demand in urban areas",
            "expected_yield_per_acre": "5-6 tonnes",
            "expected_profit_inr": 200000,
            "best_season": "Year-round (peak harvest June-November)",
            "care_tips": "Needs concrete/wooden trellis support, well-drained soil, monthly organic fertilizer",
            "market_demand_score": 8,
            "grow_duration_days": 365,
        }
