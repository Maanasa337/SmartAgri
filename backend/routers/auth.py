"""
Auth router — signup, login, and current user.
"""
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

from db.mongodb import users_col
from models.user import UserCreate, UserLogin, UserResponse, Token
from services.soil_service import fetch_soil_data
from services.weather_service import fetch_weather_data
from services.cluster_service import assign_cluster

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "smartagri_jwt_secret_key_2026_super_secure")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def create_token(user_id: str, email: str) -> str:
    """Create a JWT token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(request: Request) -> dict:
    """Dependency to extract and validate JWT from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    from bson import ObjectId
    user = await users_col().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user["id"] = str(user["_id"])
    return user


def _user_to_response(user: dict) -> dict:
    """Convert MongoDB user doc to response dict."""
    return {
        "id": str(user.get("_id", user.get("id", ""))),
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "present_crop": user.get("present_crop", ""),
        "present_crop_stage": user.get("present_crop_stage", ""),
        "land_acres": user.get("land_acres", 0),
        "gps_coordinates": user.get("gps_coordinates", {}),
        "past_crop": user.get("past_crop", ""),
        "past_disease": user.get("past_disease", ""),
        "soil_data": user.get("soil_data"),
        "weather_data": user.get("weather_data"),
        "cluster_id": user.get("cluster_id"),
    }


@router.post("/signup", response_model=Token)
async def signup(data: UserCreate):
    """Register a new farmer user."""
    col = users_col()

    # Check if email already exists
    existing = await col.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed = pwd_context.hash(data.password)

    # Build user document
    user_doc = {
        "username": data.username,
        "email": data.email,
        "password_hash": hashed,
        "present_crop": data.present_crop,
        "present_crop_stage": data.present_crop_stage.value,
        "land_acres": data.land_acres,
        "gps_coordinates": {"lat": data.gps_coordinates.lat, "lng": data.gps_coordinates.lng},
        "past_crop": data.past_crop,
        "past_disease": data.past_disease,
        "soil_data": None,
        "weather_data": None,
        "cluster_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Insert user
    result = await col.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Fire async background tasks (soil, weather, cluster)
    import asyncio

    async def enrich_user():
        try:
            lat = data.gps_coordinates.lat
            lng = data.gps_coordinates.lng

            # Fetch soil and weather in parallel
            soil_task = fetch_soil_data(lat, lng)
            weather_task = fetch_weather_data(lat, lng)
            cluster_task = assign_cluster(lat, lng)

            soil_data, weather_data, cluster_id = await asyncio.gather(
                soil_task, weather_task, cluster_task
            )

            # Update user document
            from bson import ObjectId
            await col.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "soil_data": soil_data,
                    "weather_data": weather_data,
                    "cluster_id": cluster_id,
                }}
            )
            print(f"✅ User {user_id} enriched: soil + weather + cluster={cluster_id}")
        except Exception as e:
            print(f"⚠ Background enrichment failed for {user_id}: {e}")

    # Launch enrichment without blocking
    asyncio.create_task(enrich_user())

    # Create token
    token = create_token(user_id, data.email)

    user_doc["id"] = user_id
    return Token(
        access_token=token,
        user=UserResponse(**_user_to_response(user_doc))
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """Authenticate existing user."""
    col = users_col()
    user = await col.find_one({"email": data.email})

    if not user or not pwd_context.verify(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_token(user_id, data.email)

    return Token(
        access_token=token,
        user=UserResponse(**_user_to_response(user))
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return _user_to_response(current_user)
