"""
Comprehensive seed script for markets and prices.
This script populates the database with many markets and historical price data.
Usage: python scripts/seed_comprehensive_data.py
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


# Comprehensive crop data
CROPS_DATA = [
    {"name": "Maize", "crop_type": "Grain"},
    {"name": "Wheat", "crop_type": "Grain"},
    {"name": "Teff", "crop_type": "Grain"},
    {"name": "Barley", "crop_type": "Grain"},
    {"name": "Sorghum", "crop_type": "Grain"},
    {"name": "Tomato", "crop_type": "Vegetable"},
    {"name": "Onion", "crop_type": "Vegetable"},
    {"name": "Potato", "crop_type": "Vegetable"},
    {"name": "Cabbage", "crop_type": "Vegetable"},
    {"name": "Carrot", "crop_type": "Vegetable"},
    {"name": "Coffee", "crop_type": "Cash Crop"},
    {"name": "Sesame", "crop_type": "Cash Crop"},
    {"name": "Chickpea", "crop_type": "Legume"},
    {"name": "Lentil", "crop_type": "Legume"},
    {"name": "Bean", "crop_type": "Legume"},
]

# Comprehensive market data (Ethiopian markets)
MARKETS_DATA = [
    # Addis Ababa Region
    {"name": "Merkato", "region": "Addis Ababa"},
    {"name": "Shola Market", "region": "Addis Ababa"},
    {"name": "Kera Market", "region": "Addis Ababa"},
    {"name": "Piazza Market", "region": "Addis Ababa"},
    
    # Oromia Region
    {"name": "Adama", "region": "Oromia"},
    {"name": "Bishoftu", "region": "Oromia"},
    {"name": "Jimma", "region": "Oromia"},
    {"name": "Nekemte", "region": "Oromia"},
    {"name": "Shashamane", "region": "Oromia"},
    {"name": "Ambo", "region": "Oromia"},
    
    # Amhara Region
    {"name": "Bahir Dar", "region": "Amhara"},
    {"name": "Gondar", "region": "Amhara"},
    {"name": "Dessie", "region": "Amhara"},
    {"name": "Kombolcha", "region": "Amhara"},
    {"name": "Debre Markos", "region": "Amhara"},
    
    # Tigray Region
    {"name": "Mekelle", "region": "Tigray"},
    {"name": "Adigrat", "region": "Tigray"},
    {"name": "Shire", "region": "Tigray"},
    
    # SNNPR (Southern Nations, Nationalities, and Peoples' Region)
    {"name": "Hawassa", "region": "SNNPR"},
    {"name": "Arba Minch", "region": "SNNPR"},
    {"name": "Sodo", "region": "SNNPR"},
    {"name": "Dilla", "region": "SNNPR"},
    
    # Somali Region
    {"name": "Jijiga", "region": "Somali"},
    {"name": "Dire Dawa", "region": "Dire Dawa"},
    
    # Afar Region
    {"name": "Semera", "region": "Afar"},
    
    # Gambela Region
    {"name": "Gambela", "region": "Gambela"},
    
    # Harari Region
    {"name": "Harar", "region": "Harari"},
]


def seed_crops(db: Session):
    """Seed crops."""
    print("\n🌾 Seeding crops...")
    seeded_count = 0
    skipped_count = 0
    
    for crop_data in CROPS_DATA:
        statement = select(Crop).where(Crop.name == crop_data["name"])
        existing_crop = db.exec(statement).first()
        
        if not existing_crop:
            crop = Crop(**crop_data)
            db.add(crop)
            print(f"  ✓ Added: {crop_data['name']} ({crop_data['crop_type']})")
            seeded_count += 1
        else:
            print(f"  ⊙ Exists: {crop_data['name']}")
            skipped_count += 1
    
    db.commit()
    print(f"\n  Crops: {seeded_count} added, {skipped_count} already exist")
    return seeded_count


def seed_markets(db: Session):
    """Seed markets."""
    print("\n🏪 Seeding markets...")
    seeded_count = 0
    skipped_count = 0
    
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
            seeded_count += 1
        else:
            print(f"  ⊙ Exists: {market_data['name']}, {market_data['region']}")
            skipped_count += 1
    
    db.commit()
    print(f"\n  Markets: {seeded_count} added, {skipped_count} already exist")
    return seeded_count


def generate_price_data(crop_id: int, market_id: int, base_price: float, days: int = 90):
    """
    Generate historical price data for a crop-market combination.
    Prices vary realistically with some trend and random fluctuations.
    """
    prices = []
    today = date.today()
    
    # Start from 'days' ago
    start_date = today - timedelta(days=days)
    
    # Base price with some variation per market/crop
    current_price = base_price
    
    for i in range(days):
        price_date = start_date + timedelta(days=i)
        
        # Add some realistic price variation:
        # - Small daily fluctuations (±2-5%)
        # - Weekly trends (gradual increase/decrease)
        # - Seasonal patterns (slight variation)
        
        # Daily fluctuation
        fluctuation = random.uniform(-0.03, 0.03)  # ±3%
        
        # Weekly trend (every 7 days, slight trend)
        if i % 7 == 0:
            trend = random.uniform(-0.02, 0.05)  # Weekly trend
        else:
            trend = 0
        
        # Apply changes
        current_price = current_price * (1 + fluctuation + trend)
        
        # Ensure price stays within reasonable bounds (50% to 200% of base)
        current_price = max(base_price * 0.5, min(base_price * 2.0, current_price))
        
        # Round to 2 decimal places
        price = round(current_price, 2)
        
        # Source: mix of manual, api, and market_officer
        sources = ["manual", "api", "market_officer"]
        source = random.choice(sources)
        
        # Confidence score (0.7 to 1.0)
        confidence = round(random.uniform(0.7, 1.0), 2)
        
        prices.append({
            "crop_id": crop_id,
            "market_id": market_id,
            "price": price,
            "price_date": price_date,
            "source": source,
            "confidence_score": confidence,
        })
    
    return prices


def seed_prices(db: Session, days: int = 90):
    """Seed price data for all crop-market combinations."""
    print("\n💰 Seeding price data...")
    
    # Get all crops and markets
    crops = db.exec(select(Crop)).all()
    markets = db.exec(select(Market)).all()
    
    if not crops:
        print("  ⚠️  No crops found. Please seed crops first.")
        return 0
    
    if not markets:
        print("  ⚠️  No markets found. Please seed markets first.")
        return 0
    
    print(f"  Generating prices for {len(crops)} crops × {len(markets)} markets × {days} days...")
    
    # Base prices per crop (in ETB per kg or unit)
    base_prices = {
        "Maize": 25.0,
        "Wheat": 30.0,
        "Teff": 45.0,
        "Barley": 22.0,
        "Sorghum": 20.0,
        "Tomato": 35.0,
        "Onion": 28.0,
        "Potato": 18.0,
        "Cabbage": 15.0,
        "Carrot": 25.0,
        "Coffee": 120.0,
        "Sesame": 55.0,
        "Chickpea": 40.0,
        "Lentil": 42.0,
        "Bean": 38.0,
    }
    
    total_prices = 0
    skipped_prices = 0
    
    for crop in crops:
        base_price = base_prices.get(crop.name, 25.0)  # Default 25 ETB
        
        for market in markets:
            # Check if prices already exist for this combination
            existing = db.exec(
                select(Price).where(
                    Price.crop_id == crop.id,
                    Price.market_id == market.id
                )
            ).first()
            
            if existing:
                print(f"  ⊙ Prices exist: {crop.name} @ {market.name}")
                skipped_prices += 1
                continue
            
            # Generate price data
            # Adjust base price slightly per market (regional variation)
            market_multiplier = random.uniform(0.85, 1.15)
            adjusted_base = base_price * market_multiplier
            
            price_data_list = generate_price_data(
                crop.id,
                market.id,
                adjusted_base,
                days
            )
            
            # Add prices in batches for efficiency
            for price_data in price_data_list:
                price = Price(**price_data)
                db.add(price)
            
            total_prices += len(price_data_list)
            print(f"  ✓ Added {days} prices: {crop.name} @ {market.name}")
            
            # Commit in batches to avoid memory issues
            if total_prices % 500 == 0:
                db.commit()
                print(f"    (Committed {total_prices} prices so far...)")
    
    db.commit()
    print(f"\n  Prices: {total_prices} added, {skipped_prices} combinations skipped")
    return total_prices


def seed_all(days: int = 90):
    """Seed all data: crops, markets, and prices."""
    print("=" * 60)
    print("🌱 Comprehensive Database Seeding")
    print("=" * 60)
    
    # Initialize database
    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize database: {e}")
        print("   Continuing anyway...")
    
    with Session(engine) as session:
        # Seed crops
        crops_count = seed_crops(session)
        
        # Seed markets
        markets_count = seed_markets(session)
        
        # Seed prices (only if we have crops and markets)
        if crops_count > 0 or markets_count > 0:
            prices_count = seed_prices(session, days=days)
        else:
            print("\n⚠️  Skipping price seeding - no new crops or markets added")
            prices_count = 0
    
    print("\n" + "=" * 60)
    print("✅ Seeding completed!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  • Crops: Checked {len(CROPS_DATA)} crops")
    print(f"  • Markets: Checked {len(MARKETS_DATA)} markets")
    print(f"  • Prices: Generated {days} days of historical data per combination")
    print("\n💡 Tip: Run this script multiple times safely - it skips existing data.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed database with comprehensive data")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days of historical price data to generate (default: 90)"
    )
    
    args = parser.parse_args()
    
    seed_all(days=args.days)
