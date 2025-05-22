from app import app, db
from models import Product

def update_all_product_ratings():
    with app.app_context():
        products = Product.query.all()
        for product in products:
            product.update_rating_stats()
        print("Updated ratings for all products")
