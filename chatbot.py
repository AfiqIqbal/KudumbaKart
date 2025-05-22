from knowledge_base import knowledge_base
import random
from models import db, Product, KudumbashreeUnit, User

class KudumbaKartBot:
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.context = ""
        self.products = {}
        self.units = {}
        
    def init_app(self, app):
        """Initialize the chatbot with the Flask app"""
        try:
            with app.app_context():
                # Load all products
                products = Product.query.filter_by(is_active=True).all()
                for product in products:
                    seller = User.query.get(product.seller_id)
                    unit = seller.unit if seller else None
                    
                    self.products[product.name.lower()] = {
                        "name": product.name,
                        "price": product.price,
                        "description": product.description,
                        "category": product.category,
                        "rating": product.average_rating,
                        "reviews": product.rating_count,
                        "seller": seller.username if seller else "Unknown",
                        "unit_name": unit.name if unit else "Unknown",
                        "unit_district": unit.district if unit else "Unknown",
                        "unit_panchayat": unit.panchayat if unit else "Unknown"
                    }
                
                # Load all Kudumbashree units
                units = KudumbashreeUnit.query.all()
                for unit in units:
                    self.units[unit.name.lower()] = {
                        "name": unit.name,
                        "district": unit.district,
                        "panchayat": unit.panchayat,
                        "registration": unit.registration_number
                    }
                
                print("Chatbot initialized successfully with product and unit data")
                return True
        except Exception as e:
            print(f"Error initializing chatbot: {str(e)}")
            return False

    def get_product_info(self, message):
        """Get product information from message"""
        message = message.lower()
        
        # Check each product
        for product_key, details in self.products.items():
            if product_key in message:
                response = f"""Yes! We have {details['name']} 🎉

💰 Price: ₹{details['price']:.2f}
⭐ Rating: {details['rating']:.1f} ({details['reviews']} reviews)
📝 Description: {details['description']}

🏢 Seller Information:
• Seller: {details['seller']}
• Unit: {details['unit_name']}
• Location: {details['unit_district']}, {details['unit_panchayat']}

Would you like to:
1. Add to cart
2. View similar products
3. Check other variants

Just let me know what you'd prefer!"""
                return response

        # If no specific product found
        return """Here are our popular products:

1. 🍌 Banana Chips
2. 🥥 Coconut Oil
3. 🌶️ Black Pepper

Which one would you like to know more about?"""

    def get_unit_info(self):
        """Get information about all units"""
        response = f"🏢 We have {len(self.units)} Kudumbashree units:\n\n"
        
        for name, details in self.units.items():
            response += f"""📍 {details['name']}:
• District: {details['district']}
• Panchayat: {details['panchayat']}
• Registration: {details['registration']}\n\n"""
        
        return response.strip()

    def handle_message(self, message):
        """Process user message and generate response"""
        try:
            message = message.lower()
            
            # Check for product queries
            if any(product in message for product in self.products.keys()):
                return self.get_product_info(message)
            
            # Check for unit queries
            if 'unit' in message or 'units' in message or 'kudumbashree' in message:
                return self.get_unit_info()
            
            # Default response with menu
            return """I can help you with:

1. 🛍️ Our Products and Prices
2. 🏢 Kudumbashree Units
3. 📞 Contact Information

What would you like to know about?"""
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return """I apologize for the confusion. Let me help you with:

1. 🛍️ Popular Products
2. 🏢 Kudumbashree Units
3. 📞 Contact Information

What would you like to know about?"""

def get_bot():
    return KudumbaKartBot()
