import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Product, CartItem, Review

def remove_seller_products():
    """Remove all products from seller 1 and 2."""
    with app.app_context():
        # Get products from seller 1 and 2
        products = Product.query.filter(Product.seller_id.in_([1, 2])).all()
        
        for product in products:
            # First remove cart items for this product
            cart_items = CartItem.query.filter_by(product_id=product.id).all()
            for cart_item in cart_items:
                print(f"Removing cart item for product: {product.name}")
                db.session.delete(cart_item)
            
            # Remove reviews for this product
            reviews = Review.query.filter_by(product_id=product.id).all()
            for review in reviews:
                print(f"Removing review for product: {product.name}")
                db.session.delete(review)
            
            # Then remove the product
            print(f"Removing product: {product.name} (Seller ID: {product.seller_id})")
            db.session.delete(product)
        
        db.session.commit()
        print("Products from seller 1 and 2 removed successfully!")

if __name__ == '__main__':
    remove_seller_products()
