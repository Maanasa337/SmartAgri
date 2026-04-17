"""
Seed script — Populate MongoDB with realistic India-relevant data.
Run: python -m db.seed  (from backend/)
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

# Add parent to path so we can import db
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "smartagri_db")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    """Seed all collections with realistic data."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB]

    print("🌱 Seeding SmartAgri database...")

    # ── 1. USERS — 10 Tamil Nadu farmers ──────────────────────────────────────
    users_col = db["users"]
    await users_col.delete_many({})

    farmers = [
        {
            "username": "Murugan Selvam",
            "email": "murugan.selvam@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "paddy",
            "present_crop_stage": "vegetative",
            "land_acres": 5.0,
            "gps_coordinates": {"lat": 10.7870, "lng": 79.1378},  # Thanjavur
            "past_crop": "groundnut",
            "past_disease": "blast",
            "soil_data": {"nitrogen_kg_ha": 290, "phosphorus_kg_ha": 24, "potassium_kg_ha": 195, "ph": 7.1, "organic_carbon_pct": 0.58, "texture": "Clay", "source": "SoilGrids"},
            "weather_data": {"temp": 32, "humidity": 72, "condition": "partly cloudy"},
            "cluster_id": "cluster_10.79_79.14",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Lakshmi Devi",
            "email": "lakshmi.devi@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "sugarcane",
            "present_crop_stage": "vegetative",
            "land_acres": 8.0,
            "gps_coordinates": {"lat": 10.8050, "lng": 79.1500},  # Thanjavur
            "past_crop": "paddy",
            "past_disease": "red rot",
            "soil_data": {"nitrogen_kg_ha": 310, "phosphorus_kg_ha": 28, "potassium_kg_ha": 210, "ph": 6.8, "organic_carbon_pct": 0.62, "texture": "Loamy", "source": "SoilGrids"},
            "weather_data": {"temp": 33, "humidity": 68, "condition": "sunny"},
            "cluster_id": "cluster_10.79_79.14",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Rajan Kumar",
            "email": "rajan.kumar@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "banana",
            "present_crop_stage": "flowering",
            "land_acres": 3.5,
            "gps_coordinates": {"lat": 10.7905, "lng": 79.1320},  # Thanjavur
            "past_crop": "turmeric",
            "past_disease": "panama wilt",
            "soil_data": {"nitrogen_kg_ha": 275, "phosphorus_kg_ha": 22, "potassium_kg_ha": 250, "ph": 6.5, "organic_carbon_pct": 0.70, "texture": "Loamy", "source": "SoilGrids"},
            "weather_data": {"temp": 31, "humidity": 75, "condition": "cloudy"},
            "cluster_id": "cluster_10.79_79.14",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Kavitha Subramanian",
            "email": "kavitha.s@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "turmeric",
            "present_crop_stage": "sowing",
            "land_acres": 2.5,
            "gps_coordinates": {"lat": 10.8155, "lng": 78.6960},  # Trichy
            "past_crop": "paddy",
            "past_disease": "rhizome rot",
            "soil_data": {"nitrogen_kg_ha": 260, "phosphorus_kg_ha": 18, "potassium_kg_ha": 170, "ph": 7.3, "organic_carbon_pct": 0.48, "texture": "Sandy", "source": "SoilGrids"},
            "weather_data": {"temp": 34, "humidity": 60, "condition": "hot"},
            "cluster_id": "cluster_10.82_78.70",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Senthil Nathan",
            "email": "senthil.n@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "groundnut",
            "present_crop_stage": "flowering",
            "land_acres": 4.0,
            "gps_coordinates": {"lat": 10.8200, "lng": 78.7100},  # Trichy
            "past_crop": "maize",
            "past_disease": "tikka disease",
            "soil_data": {"nitrogen_kg_ha": 240, "phosphorus_kg_ha": 20, "potassium_kg_ha": 160, "ph": 6.9, "organic_carbon_pct": 0.52, "texture": "Sandy", "source": "SoilGrids"},
            "weather_data": {"temp": 33, "humidity": 62, "condition": "clear"},
            "cluster_id": "cluster_10.82_78.70",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Anitha Pandian",
            "email": "anitha.p@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "paddy",
            "present_crop_stage": "harvest",
            "land_acres": 6.0,
            "gps_coordinates": {"lat": 10.8300, "lng": 78.6850},  # Trichy
            "past_crop": "sugarcane",
            "past_disease": "sheath blight",
            "soil_data": {"nitrogen_kg_ha": 300, "phosphorus_kg_ha": 26, "potassium_kg_ha": 200, "ph": 7.0, "organic_carbon_pct": 0.60, "texture": "Clay", "source": "SoilGrids"},
            "weather_data": {"temp": 32, "humidity": 70, "condition": "partly cloudy"},
            "cluster_id": "cluster_10.82_78.70",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Vel Murugan",
            "email": "vel.murugan@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "sugarcane",
            "present_crop_stage": "sowing",
            "land_acres": 10.0,
            "gps_coordinates": {"lat": 9.9252, "lng": 78.1198},  # Madurai
            "past_crop": "paddy",
            "past_disease": "smut",
            "soil_data": {"nitrogen_kg_ha": 280, "phosphorus_kg_ha": 25, "potassium_kg_ha": 190, "ph": 7.5, "organic_carbon_pct": 0.45, "texture": "Loamy", "source": "SoilGrids"},
            "weather_data": {"temp": 35, "humidity": 55, "condition": "hot and dry"},
            "cluster_id": "cluster_9.93_78.12",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Priya Ramasamy",
            "email": "priya.r@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "banana",
            "present_crop_stage": "vegetative",
            "land_acres": 4.5,
            "gps_coordinates": {"lat": 9.9300, "lng": 78.1250},  # Madurai
            "past_crop": "groundnut",
            "past_disease": "sigatoka leaf spot",
            "soil_data": {"nitrogen_kg_ha": 270, "phosphorus_kg_ha": 21, "potassium_kg_ha": 230, "ph": 6.7, "organic_carbon_pct": 0.65, "texture": "Loamy", "source": "SoilGrids"},
            "weather_data": {"temp": 34, "humidity": 58, "condition": "sunny"},
            "cluster_id": "cluster_9.93_78.12",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Karthik Ganesan",
            "email": "karthik.g@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "paddy",
            "present_crop_stage": "sowing",
            "land_acres": 7.0,
            "gps_coordinates": {"lat": 9.9180, "lng": 78.1100},  # Madurai
            "past_crop": "banana",
            "past_disease": "brown spot",
            "soil_data": {"nitrogen_kg_ha": 295, "phosphorus_kg_ha": 23, "potassium_kg_ha": 185, "ph": 7.2, "organic_carbon_pct": 0.55, "texture": "Clay", "source": "SoilGrids"},
            "weather_data": {"temp": 33, "humidity": 65, "condition": "partly cloudy"},
            "cluster_id": "cluster_9.93_78.12",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "username": "Selvi Krishnan",
            "email": "selvi.k@example.com",
            "password_hash": pwd_context.hash("farmer123"),
            "present_crop": "groundnut",
            "present_crop_stage": "vegetative",
            "land_acres": 3.0,
            "gps_coordinates": {"lat": 10.7950, "lng": 79.1400},  # Thanjavur
            "past_crop": "paddy",
            "past_disease": "collar rot",
            "soil_data": {"nitrogen_kg_ha": 255, "phosphorus_kg_ha": 19, "potassium_kg_ha": 165, "ph": 7.0, "organic_carbon_pct": 0.50, "texture": "Sandy", "source": "SoilGrids"},
            "weather_data": {"temp": 31, "humidity": 73, "condition": "overcast"},
            "cluster_id": "cluster_10.79_79.14",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]

    await users_col.insert_many(farmers)
    print(f"  ✅ {len(farmers)} farmer users seeded")

    # ── 2. MARKET TRENDS — 30 days × 5 crops ─────────────────────────────────
    trends_col = db["market_trends"]
    await trends_col.delete_many({})

    crops_data = {
        "paddy":     {"base": 2100, "variation": 150},
        "sugarcane": {"base": 350,  "variation": 30},
        "banana":    {"base": 1800, "variation": 200},
        "turmeric":  {"base": 8500, "variation": 800},
        "groundnut": {"base": 5800, "variation": 400},
    }

    import random
    random.seed(42)
    trends = []
    now = datetime.now(timezone.utc)

    for crop_name, price_info in crops_data.items():
        base = price_info["base"]
        var = price_info["variation"]
        for day_offset in range(30):
            date = now - timedelta(days=29 - day_offset)
            # Simulate realistic price movement
            noise = random.uniform(-var, var)
            trend_factor = 1 + (day_offset - 15) * 0.002  # slight upward trend
            price = round(base * trend_factor + noise, 2)

            demand_choices = ["Low", "Medium", "High", "Very High"]
            demand = random.choice(demand_choices) if price > base else random.choice(demand_choices[:2])

            trend_dir = "up" if noise > 0 else "down" if noise < -var * 0.3 else "stable"

            trends.append({
                "crop_name": crop_name,
                "price_per_quintal": price,
                "demand_level": demand,
                "trend_direction": trend_dir,
                "timestamp": date.isoformat(),
                "market_name": random.choice(["Thanjavur APMC", "Trichy Mandi", "Madurai Market"]),
            })

    await trends_col.insert_many(trends)
    print(f"  ✅ {len(trends)} market trend records seeded (5 crops × 30 days)")

    # ── 3. PEST ALERTS — 5 records ────────────────────────────────────────────
    pest_col = db["pest_alerts"]
    await pest_col.delete_many({})

    pest_records = [
        {
            "reported_by_user_id": "seed_user_1",
            "reporter_name": "Murugan Selvam",
            "crop": "paddy",
            "pest_name": "Brown Planthopper",
            "severity": 7,
            "location_coords": {"lat": 10.7870, "lng": 79.1378},
            "timestamp": (now - timedelta(days=2)).isoformat(),
            "notified_cluster": "cluster_10.79_79.14",
        },
        {
            "reported_by_user_id": "seed_user_4",
            "reporter_name": "Kavitha Subramanian",
            "crop": "turmeric",
            "pest_name": "Shoot Borer",
            "severity": 5,
            "location_coords": {"lat": 10.8155, "lng": 78.6960},
            "timestamp": (now - timedelta(days=5)).isoformat(),
            "notified_cluster": "cluster_10.82_78.70",
        },
        {
            "reported_by_user_id": "seed_user_3",
            "reporter_name": "Rajan Kumar",
            "crop": "banana",
            "pest_name": "Banana Aphid",
            "severity": 4,
            "location_coords": {"lat": 10.7905, "lng": 79.1320},
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "notified_cluster": "cluster_10.79_79.14",
        },
        {
            "reported_by_user_id": "seed_user_7",
            "reporter_name": "Vel Murugan",
            "crop": "sugarcane",
            "pest_name": "Woolly Aphid",
            "severity": 8,
            "location_coords": {"lat": 9.9252, "lng": 78.1198},
            "timestamp": (now - timedelta(days=3)).isoformat(),
            "notified_cluster": "cluster_9.93_78.12",
        },
        {
            "reported_by_user_id": "seed_user_5",
            "reporter_name": "Senthil Nathan",
            "crop": "groundnut",
            "pest_name": "Leaf Miner",
            "severity": 3,
            "location_coords": {"lat": 10.8200, "lng": 78.7100},
            "timestamp": (now - timedelta(days=7)).isoformat(),
            "notified_cluster": "cluster_10.82_78.70",
        },
    ]

    await pest_col.insert_many(pest_records)
    print(f"  ✅ {len(pest_records)} pest alert records seeded")

    # ── 4. PRODUCTS — 8 pesticides/fertilizers ────────────────────────────────
    products_col = db["products"]
    await products_col.delete_many({})

    products = [
        {"name": "Neem Oil Spray (1L)", "type": "organic", "target_pest": "Aphid, Whitefly, general", "price": 280, "delivery_days": 2, "in_stock": True},
        {"name": "Chlorantraniliprole 18.5% SC (100ml)", "type": "chemical", "target_pest": "Stem Borer, Leaf Folder, Brown Planthopper", "price": 520, "delivery_days": 2, "in_stock": True},
        {"name": "Imidacloprid 17.8% SL (250ml)", "type": "chemical", "target_pest": "Brown Planthopper, Woolly Aphid, Aphid", "price": 380, "delivery_days": 2, "in_stock": True},
        {"name": "Trichoderma Viride (1kg)", "type": "organic", "target_pest": "Root Rot, Wilt, Rhizome Rot, general", "price": 350, "delivery_days": 2, "in_stock": True},
        {"name": "Pseudomonas Fluorescens (1kg)", "type": "organic", "target_pest": "Blast, Sheath Blight, general", "price": 320, "delivery_days": 2, "in_stock": True},
        {"name": "Carbendazim 50% WP (500g)", "type": "chemical", "target_pest": "Blast, Sheath Blight, Leaf Spot, Sigatoka", "price": 290, "delivery_days": 2, "in_stock": True},
        {"name": "Pheromone Trap Kit (5 units)", "type": "organic", "target_pest": "Shoot Borer, Leaf Miner, Stem Borer", "price": 450, "delivery_days": 2, "in_stock": True},
        {"name": "Yellow Sticky Trap Pack (20 sheets)", "type": "organic", "target_pest": "Whitefly, Aphid, Leaf Miner, general", "price": 180, "delivery_days": 2, "in_stock": True},
    ]

    await products_col.insert_many(products)
    print(f"  ✅ {len(products)} product records seeded")

    # ── 5. VENDORS — 5 local vendors ──────────────────────────────────────────
    vendors_col = db["vendors"]
    await vendors_col.delete_many({})

    vendors = [
        {
            "name": "Thanjai Agro Traders",
            "location": "East Gate, Thanjavur",
            "crops_accepted": ["paddy", "groundnut", "banana", "Dragon Fruit"],
            "contact": "+91 98765 43210",
            "email": "thanjai.agro@example.com",
            "active": True,
        },
        {
            "name": "Cauvery Fresh Produce",
            "location": "Market Road, Trichy",
            "crops_accepted": ["paddy", "sugarcane", "turmeric", "Moringa", "Quinoa"],
            "contact": "+91 87654 32109",
            "email": "cauvery.fresh@example.com",
            "active": True,
        },
        {
            "name": "Madurai Organic Hub",
            "location": "Periyar Bus Stand, Madurai",
            "crops_accepted": ["banana", "turmeric", "groundnut", "Passion Fruit", "Moringa"],
            "contact": "+91 76543 21098",
            "email": "madurai.organic@example.com",
            "active": True,
        },
        {
            "name": "Delta Farm Exports",
            "location": "Kumbakonam Road, Thanjavur",
            "crops_accepted": ["paddy", "sugarcane", "turmeric", "Marigold", "Dragon Fruit"],
            "contact": "+91 65432 10987",
            "email": "delta.exports@example.com",
            "active": True,
        },
        {
            "name": "TN Agri Fresh Pvt Ltd",
            "location": "Collector Office Road, Trichy",
            "crops_accepted": ["banana", "groundnut", "paddy", "Quinoa", "Passion Fruit"],
            "contact": "+91 54321 09876",
            "email": "tn.agrifresh@example.com",
            "active": True,
        },
    ]

    await vendors_col.insert_many(vendors)
    print(f"  ✅ {len(vendors)} vendor records seeded")

    # ── 6. EXOTIC RECOMMENDATIONS ─────────────────────────────────────────────
    exotic_col = db["exotic_recommendations"]
    await exotic_col.delete_many({})

    exotic_recs = [
        {
            "user_id": "seed_global",
            "crop_name": "Dragon Fruit",
            "why_suitable": "Thrives in Tamil Nadu's warm climate with well-drained soil. Growing demand in Tier-1 cities. Low water requirement compared to paddy.",
            "expected_yield_per_acre": "5-6 tonnes",
            "expected_profit_inr": 250000,
            "best_season": "Year-round (main harvest June-November)",
            "care_tips": "Requires concrete/wooden trellis support, moderate watering, full sun exposure. Apply organic manure quarterly.",
            "market_demand_score": 8,
            "grow_duration_days": 365,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "user_id": "seed_global",
            "crop_name": "Moringa",
            "why_suitable": "Native to Tamil Nadu, extremely drought-tolerant. High export demand for moringa powder and oil. Grows in poor soil conditions.",
            "expected_yield_per_acre": "4-5 tonnes leaves",
            "expected_profit_inr": 180000,
            "best_season": "Year-round harvest, plant in June-July",
            "care_tips": "Minimal irrigation needed. Prune monthly for leaf harvest. Space plants 3m apart.",
            "market_demand_score": 9,
            "grow_duration_days": 90,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "user_id": "seed_global",
            "crop_name": "Marigold (Saffron Substitute)",
            "why_suitable": "Marigold extract is used as natural food colorant, substitute for expensive saffron. Temple demand ensures baseline sales.",
            "expected_yield_per_acre": "8-10 tonnes flowers",
            "expected_profit_inr": 150000,
            "best_season": "October-March (Rabi season)",
            "care_tips": "Well-drained soil, moderate watering. Harvest flowers early morning. Dry in shade for colorant extraction.",
            "market_demand_score": 7,
            "grow_duration_days": 120,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "user_id": "seed_global",
            "crop_name": "Quinoa",
            "why_suitable": "Superfood with growing urban demand. Adapts to Tamil Nadu's climate. Higher price per kg than traditional grains.",
            "expected_yield_per_acre": "1.5-2 tonnes",
            "expected_profit_inr": 120000,
            "best_season": "November-February (Rabi season)",
            "care_tips": "Sandy-loam soil preferred. Light irrigation. Harvest when seeds easily detach from panicle.",
            "market_demand_score": 6,
            "grow_duration_days": 110,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "user_id": "seed_global",
            "crop_name": "Passion Fruit",
            "why_suitable": "High-value fruit with growing juice industry demand. Suitable for Madurai belt climate. Low maintenance after establishment.",
            "expected_yield_per_acre": "8-10 tonnes",
            "expected_profit_inr": 200000,
            "best_season": "Year-round after 18 months establishment",
            "care_tips": "Needs trellis/pandal system. Deep watering weekly. Prune dead vines after harvest.",
            "market_demand_score": 7,
            "grow_duration_days": 540,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]

    await exotic_col.insert_many(exotic_recs)
    print(f"  ✅ {len(exotic_recs)} exotic crop recommendations seeded")

    # ── Done ──────────────────────────────────────────────────────────────────
    print("\n🎉 Database seeding complete!")
    print(f"   Database: {MONGODB_DB}")
    print(f"   Collections: users, market_trends, pest_alerts, products, vendors, exotic_recommendations")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
