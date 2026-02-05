"""
Seed script for initial data (crops, markets, and prices).
Usage: python scripts/seed_data.py

Works with PostgreSQL on Render using DATABASE_URL environment variable.
Safe to re-run - skips existing data.
"""
import sys
import os
from datetime import date, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlmodel import Session, select
from database import engine, init_db
from models.crop import Crop
from models.market import Market
from models.price import Price
from config import settings


# Crops data (8 crops)
CROPS_DATA = [
    {"name": "Maize", "crop_type": "Grain"},
    {"name": "Wheat", "crop_type": "Grain"},
    {"name": "Teff", "crop_type": "Grain"},
    {"name": "Tomato", "crop_type": "Vegetable"},
    {"name": "Onion", "crop_type": "Vegetable"},
    {"name": "Potato", "crop_type": "Vegetable"},
    {"name": "Coffee", "crop_type": "Cash Crop"},
    {"name": "Sesame", "crop_type": "Cash Crop"},
]

# Markets data (10 markets)
MARKETS_DATA = [
    {"name": "Merkato", "region": "Addis Ababa"},
    {"name": "Adama", "region": "Oromia"},
    {"name": "Bahir Dar", "region": "Amhara"},
    {"name": "Gondar", "region": "Amhara"},
    {"name": "Jimma", "region": "Oromia"},
    {"name": "Hawassa", "region": "SNNPR"},
    {"name": "Mekelle", "region": "Tigray"},
    {"name": "Dessie", "region": "Amhara"},
    {"name": "Shashamane", "region": "Oromia"},
    {"name": "Dire Dawa", "region": "Dire Dawa"},
]

# Base prices per crop (ETB per kg)
BASE_PRICES = {
    "Maize": 25.0,
    "Wheat": 30.0,
    "Teff": 45.0,
    "Tomato": 35.0,
    "Onion": 28.0,
    "Potato": 18.0,
    "Coffee": 120.0,
    "Sesame": 55.0,
}


def seed_crops(db: Session):
    """Seed crops."""
    print("\n🌾 Seeding crops...")
    added = 0
    skipped = 0
    
    for crop_data in CROPS_DATA:
        statement = select(Crop).where(Crop.name == crop_data["name"])
        existing_crop = db.exec(statement).first()
        
        if not existing_crop:
            crop = Crop(**crop_data)
            db.add(crop)
            print(f"  ✓ Added: {crop_data['name']} ({crop_data['crop_type']})")
            added += 1
        else:
            print(f"  ⊙ Exists: {crop_data['name']}")
            skipped += 1
    
    db.commit()
    print(f"  Result: {added} added, {skipped} already exist")
    return added


def seed_markets(db: Session):
    """Seed markets."""
    print("\n🏪 Seeding markets...")
    added = 0
    skipped = 0
    
    for market_data in MARKETS_DATA:
        statement = select(Market).where(
            Market.name == market_data["name"],
            Market.region == market_data["region"]
        )
        existing_market = db.exec(statement).first()
        
        if not existing_market:
            market = Market(**market_data)
            db.add(market)
            print(f"  ✓ Added: {market_data['name']}, {market_data['region']}")
            added += 1
        else:
            print(f"  ⊙ Exists: {market_data['name']}, {market_data['region']}")
            skipped += 1
    
    db.commit()
    print(f"  Result: {added} added, {skipped} already exist")
    return added


def seed_prices(db: Session, days: int = 60):
    """Seed price data for all crop-market combinations."""
    print(f"\n💰 Seeding prices ({days} days of data)...")
    
    # Get all crops and markets
    crops = db.exec(select(Crop)).all()
    markets = db.exec(select(Market)).all()
    
    if not crops:
        print("  ⚠️  No crops found. Please seed crops first.")
        return 0
    
    if not markets:
        print("  ⚠️  No markets found. Please seed markets first.")
        return 0
    
    print(f"  Generating prices for {len(crops)} crops × {len(markets)} markets...")
    
    # Sources for price data
    sources = ["manual", "api", "market_officer"]
    
    total_added = 0
    total_skipped = 0
    
    # Generate prices for each crop-market combination
    for crop in crops:
        base_price = BASE_PRICES.get(crop.name, 25.0)
        
        for market in markets:
            # Check if prices already exist for this combination
            existing = db.exec(
                select(Price).where(
                    Price.crop_id == crop.id,
                    Price.market_id == market.id
                ).limit(1)
            ).first()
            
            if existing:
                print(f"  ⊙ Prices exist: {crop.name} @ {market.name}")
                total_skipped += 1
                continue
            
            # Generate historical prices
            prices_to_add = []
            today = date.today()
            
            # Regional price variation (85% to 115% of base)
            market_multiplier = random.uniform(0.85, 1.15)
            current_price = base_price * market_multiplier
            
            for day_offset in range(days):
                price_date = today - timedelta(days=day_offset)
                
                # Add realistic price variation
                # Daily fluctuation: ±2-4%
                fluctuation = random.uniform(-0.04, 0.04)
                
                # Weekly trend: slight increase/decrease every 7 days
                if day_offset % 7 == 0:
                    trend = random.uniform(-0.03, 0.05)
                else:
                    trend = 0
                
                # Apply changes
                current_price = current_price * (1 + fluctuation + trend)
                
                # Keep price within reasonable bounds (50% to 200% of base)
                current_price = max(base_price * 0.5, min(base_price * 2.0, current_price))
                
                # Round to 2 decimal places
                price_value = round(current_price, 2)
                
                # Random source
                source = random.choice(sources)
                
                # Confidence score (0.75 to 1.0)
                confidence = round(random.uniform(0.75, 1.0), 2)
                
                prices_to_add.append(Price(
                    crop_id=crop.id,
                    market_id=market.id,
                    price=price_value,
                    price_date=price_date,
                    source=source,
                    confidence_score=confidence,
                ))
            
            # Add all prices for this combination
            for price in prices_to_add:
                db.add(price)
            
            total_added += len(prices_to_add)
            print(f"  ✓ Added {days} prices: {crop.name} @ {market.name}")
            
            # Commit periodically to avoid memory issues
            if total_added % 200 == 0:
                db.commit()
                print(f"    (Committed {total_added} prices so far...)")
    
    db.commit()
    print(f"  Result: {total_added} prices added, {total_skipped} combinations skipped")
    return total_added


def seed_all():
    """Seed all data: crops, markets, and prices."""
    print("=" * 60)
    print("🌱 Database Seeding")
    print("=" * 60)
    
    # Show database info
    db_url = settings.get_database_url()
    db_type = "PostgreSQL" if db_url.startswith("postgresql") else "SQLite"
    print(f"\n📊 Database: {db_type}")
    if db_type == "PostgreSQL":
        # Show just the host part for security
        try:
            host_part = db_url.split("@")[1].split("/")[0]
            print(f"   Host: {host_part}")
        except:
            pass
    
    # Initialize database
    try:
        init_db()
        print("✓ Database tables verified\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize database: {e}")
        print("   Continuing anyway...\n")
    
    with Session(engine) as session:
        # Seed crops
        crops_count = seed_crops(session)
        
        # Seed markets
        markets_count = seed_markets(session)
        
        # Seed prices (only if we have crops and markets)
        if crops_count > 0 or markets_count > 0 or True:  # Always try to seed prices
            prices_count = seed_prices(session, days=60)
        else:
            print("\n⚠️  Skipping price seeding - no crops or markets available")
            prices_count = 0
    
    print("\n" + "=" * 60)
    print("✅ Seeding completed!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  • Crops: {len(CROPS_DATA)} checked")
    print(f"  • Markets: {len(MARKETS_DATA)} checked")
    print(f"  • Prices: ~{prices_count} records added")
    print("\n💡 Safe to re-run - existing data is skipped.")


if __name__ == "__main__":
    seed_all()
