"""
Seed script for initial data (crops and markets).
"""
from sqlmodel import Session, select

from database import engine
from models.crop import Crop
from models.market import Market


def seed_crops(db: Session):
    """Seed example crops."""
    crops_data = [
        {"name": "Maize"},
        {"name": "Wheat"},
        {"name": "Tomato"},
    ]
    
    for crop_data in crops_data:
        # Check if crop already exists
        statement = select(Crop).where(Crop.name == crop_data["name"])
        existing_crop = db.exec(statement).first()
        
        if not existing_crop:
            crop = Crop(**crop_data)
            db.add(crop)
            print(f"Seeded crop: {crop_data['name']}")
        else:
            print(f"Crop already exists: {crop_data['name']}")
    
    db.commit()


def seed_markets(db: Session):
    """Seed example markets."""
    markets_data = [
        {"name": "Addis Ababa", "region": "Addis Ababa"},
        {"name": "Adama", "region": "Oromia"},
        {"name": "Bahir Dar", "region": "Amhara"},
    ]
    
    for market_data in markets_data:
        # Check if market already exists
        statement = select(Market).where(
            Market.name == market_data["name"],
            Market.region == market_data["region"]
        )
        existing_market = db.exec(statement).first()
        
        if not existing_market:
            market = Market(**market_data)
            db.add(market)
            print(f"Seeded market: {market_data['name']}, {market_data['region']}")
        else:
            print(f"Market already exists: {market_data['name']}, {market_data['region']}")
    
    db.commit()


def seed_all():
    """Seed all initial data."""
    with Session(engine) as session:
        print("Seeding crops...")
        seed_crops(session)
        print("\nSeeding markets...")
        seed_markets(session)
        print("\nSeeding completed!")


if __name__ == "__main__":
    seed_all()
















