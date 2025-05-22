from app import app, db, User, Product, KudumbashreeUnit
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()

        # Create sample Kudumbashree units
        units = [
            KudumbashreeUnit(
                name="Akshaya Unit",
                district="Thrissur",
                panchayat="Irinjalakuda",
                ward="5",
                description="Specializing in traditional Kerala snacks and handicrafts",
                contact_number="9876543210"
            ),
            KudumbashreeUnit(
                name="Samridhi Unit",
                district="Ernakulam",
                panchayat="Aluva",
                ward="3",
                description="Expert producers of organic vegetables and fruits",
                contact_number="9876543211"
            )
        ]
        db.session.add_all(units)
        db.session.commit()

        # Create sample users (sellers)
        users = [
            User(
                username="seller1",
                email="seller1@example.com",
                password_hash=generate_password_hash("password123"),
                is_seller=True,
                unit_id=units[0].id
            ),
            User(
                username="seller2",
                email="seller2@example.com",
                password_hash=generate_password_hash("password123"),
                is_seller=True,
                unit_id=units[1].id
            )
        ]
        db.session.add_all(users)
        db.session.commit()

        # Create sample products
        products = [
            Product(
                name="Traditional Kerala Mixture",
                description="Spicy and crunchy traditional Kerala mixture",
                price=120.00,
                category="Snacks",
                image_url="/static/images/products/mixture.jpg",
                seller_id=users[0].id
            ),
            Product(
                name="Handmade Coconut Oil",
                description="Pure and natural coconut oil made traditionally",
                price=250.00,
                category="Food",
                image_url="/static/images/products/coconut-oil.jpg",
                seller_id=users[0].id
            ),
            Product(
                name="Organic Vegetables Pack",
                description="Fresh organic vegetables from local farms",
                price=180.00,
                category="Vegetables",
                image_url="/static/images/products/vegetables.jpg",
                seller_id=users[1].id
            )
        ]
        db.session.add_all(products)
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized with sample data!")
