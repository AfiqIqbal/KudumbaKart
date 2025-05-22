from app import app, db
from models import User, Product, KudumbashreeUnit
from werkzeug.security import generate_password_hash
from datetime import datetime

def clear_data():
    """Clear existing data from all tables"""
    try:
        Product.query.delete()
        User.query.delete()
        KudumbashreeUnit.query.delete()
        db.session.commit()
    except:
        db.session.rollback()

def create_units():
    """Create Kudumbashree units"""
    units = [
        KudumbashreeUnit(
            name="Vanitha Food Products",
            district="Thiruvananthapuram",
            panchayat="Venganoor",
            registration_number="KUD001",
            formation_date=datetime(2020, 1, 1)
        ),
        KudumbashreeUnit(
            name="Samridhi Foods",
            district="Ernakulam",
            panchayat="Aluva",
            registration_number="KUD002",
            formation_date=datetime(2019, 6, 15)
        ),
        KudumbashreeUnit(
            name="Haritha Fresh",
            district="Kozhikode",
            panchayat="Kunnamangalam",
            registration_number="KUD003",
            formation_date=datetime(2021, 3, 10)
        )
    ]
    
    for unit in units:
        db.session.add(unit)
    db.session.commit()
    return units

def create_sellers(units):
    """Create seller accounts"""
    sellers = [
        User(
            username="vanitha_unit",
            email="vanitha@kudumbakart.com",
            password_hash=generate_password_hash("password123"),
            is_seller=True,
            date_joined=datetime(2025, 4, 1),
            business_name="Vanitha Food Products",
            phone="9495123456",
            address="Venganoor, Thiruvananthapuram",
            gst_number="GST001",
            unit_id=units[0].id
        ),
        User(
            username="samridhi_unit",
            email="samridhi@kudumbakart.com",
            password_hash=generate_password_hash("password123"),
            is_seller=True,
            date_joined=datetime(2025, 4, 1),
            business_name="Samridhi Foods",
            phone="9496234567",
            address="Aluva, Ernakulam",
            gst_number="GST002",
            unit_id=units[1].id
        ),
        User(
            username="haritha_unit",
            email="haritha@kudumbakart.com",
            password_hash=generate_password_hash("password123"),
            is_seller=True,
            date_joined=datetime(2025, 4, 1),
            business_name="Haritha Fresh",
            phone="9497345678",
            address="Kunnamangalam, Kozhikode",
            gst_number="GST003",
            unit_id=units[2].id
        )
    ]
    
    for seller in sellers:
        db.session.add(seller)
    db.session.commit()
    return sellers

def create_products(sellers):
    """Create products with actual images"""
    products = [
        # Vanitha Food Products
        Product(
            name="Pure Coconut Oil",
            description="Traditional cold-pressed coconut oil made from fresh Kerala coconuts. Perfect for cooking and hair care.",
            price=299.00,
            stock=50,
            category="food",
            image_url="images/products_optimized/coconut_oil.jpg",
            seller_id=sellers[0].id,
            is_active=True,
            date_added=datetime.now()
        ),
        Product(
            name="Kerala Mixture",
            description="Crunchy and spicy traditional Kerala mixture. Perfect tea-time snack.",
            price=150.00,
            stock=100,
            category="food",
            image_url="images/products_optimized/kerala_mixture.jpg",
            seller_id=sellers[0].id,
            is_active=True,
            date_added=datetime.now()
        ),
        # Samridhi Foods
        Product(
            name="Homemade Pickle",
            description="Traditional Kerala mango pickle made with authentic spices.",
            price=180.00,
            stock=40,
            category="food",
            image_url="images/products_optimized/pickle.jpg",
            seller_id=sellers[1].id,
            is_active=True,
            date_added=datetime.now()
        ),
        Product(
            name="Banana Chips",
            description="Crispy banana chips made from fresh nendran bananas.",
            price=200.00,
            stock=75,
            category="food",
            image_url="images/products_optimized/banana_chips.jpg",
            seller_id=sellers[1].id,
            is_active=True,
            date_added=datetime.now()
        ),
        # Haritha Fresh
        Product(
            name="Organic Vegetables Pack",
            description="Fresh organic vegetables grown by local farmers.",
            price=250.00,
            stock=30,
            category="food",
            image_url="images/products_optimized/organic_vegetable_pack.jpg",
            seller_id=sellers[2].id,
            is_active=True,
            date_added=datetime.now()
        ),
        Product(
            name="Curry Powder",
            description="Authentic Kerala curry powder blend made with premium spices.",
            price=180.00,
            stock=60,
            category="food",
            image_url="images/products_optimized/curry_powder.jpg",
            seller_id=sellers[2].id,
            is_active=True,
            date_added=datetime.now()
        )
    ]
    
    for product in products:
        db.session.add(product)
    db.session.commit()
    return products

if __name__ == "__main__":
    with app.app_context():
        # Clear existing data
        clear_data()
        
        # Create new data
        units = create_units()
        sellers = create_sellers(units)
        products = create_products(sellers)
        
        print("Sample data created successfully!")
