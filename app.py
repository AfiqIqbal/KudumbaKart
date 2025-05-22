from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Product, Cart, CartItem, Review, KudumbashreeUnit, Order, OrderItem
import os
import uuid
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
from chatbot import get_bot
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/images/products'

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kudumbakart@gmail.com"  # Create a new Gmail account for your app
SMTP_PASSWORD = "sycl behk sqqp wiev"    # Use an App Password from Gmail

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
# For Vercel, use in-memory SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kudumbakart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Socket.IO setup
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize chatbot
bot = get_bot()
bot.init_app(app)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=8)
    return render_template('index.html',
                         products=products,
                         title='Home')

@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    query = query.order_by(Product.date_added.desc())
    products = query.paginate(page=page, per_page=12)
    return render_template('products.html', products=products, category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    return render_template('product_detail.html', product=product, reviews=reviews, user_review=user_review)

@app.route('/cart')
@login_required
def view_cart():
    if not current_user.cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return render_template('cart.html', cart=current_user.cart)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if not current_user.cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    cart_item = CartItem.query.filter_by(
        cart_id=current_user.cart.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(
            cart_id=current_user.cart.id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        abort(403)
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Product removed from cart successfully!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        abort(403)
    
    quantity = request.form.get('quantity', type=int)
    if quantity is None or quantity < 1:
        flash('Invalid quantity!', 'error')
        return redirect(url_for('view_cart'))
    
    cart_item.quantity = quantity
    db.session.commit()
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_review:
        flash('You have already reviewed this product')
        return redirect(url_for('product_detail', product_id=product_id))
    
    review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    # Update product rating
    product.update_rating_stats()
    
    flash('Review added successfully!')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        return redirect(url_for('product_detail', product_id=review.product_id))
    
    product = review.product
    db.session.delete(review)
    db.session.commit()
    
    # Update product rating
    product.update_rating_stats()
    
    flash('Review deleted successfully!')
    return redirect(url_for('product_detail', product_id=review.product_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Get seller parameter from URL
    is_seller_param = request.args.get('seller') == '1'
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_seller = request.form.get('is_seller') == 'on'

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        # Create user
        user = User(username=username, email=email, is_seller=is_seller)
        user.set_password(password)

        # Add seller details if registering as seller
        if is_seller:
            user.business_name = request.form.get('business_name')
            user.phone = request.form.get('phone')
            user.address = request.form.get('address')
            user.gst_number = request.form.get('gst_number')

        db.session.add(user)
        db.session.commit()

        # Create cart for user
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', is_seller=is_seller_param)

@app.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if not current_user.is_seller:
        flash('Access denied. Seller account required.', 'danger')
        return redirect(url_for('index'))
    
    # Get seller's products
    products = Product.query.filter_by(seller_id=current_user.id).all()
    
    # Get seller's orders
    orders = Order.query.join(OrderItem).join(Product).filter(
        Product.seller_id == current_user.id
    ).distinct().all()
    
    # Calculate total sales
    total_sales = sum(order.total_amount for order in orders)
    
    # Count pending orders
    pending_orders = len([order for order in orders if order.status == 'pending'])
    
    return render_template('seller_dashboard.html',
                         products=products,
                         orders=orders,
                         total_sales=total_sales,
                         pending_orders=pending_orders)

@app.route('/seller/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_seller:
        flash('Access denied. Seller account required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        return render_template('add_product.html')
    
    try:
        # Handle image upload
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = f'images/products/{filename}'
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            image_path = None
        
        # Create product
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            category=request.form['category'],
            image_url=image_path,
            seller_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error adding product. Please try again.', 'danger')
        return redirect(url_for('add_product'))

@app.route('/seller/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_seller:
        return jsonify({'error': 'Seller account required'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Error deleting product'}), 500

@app.route('/seller/<int:seller_id>')
def seller_profile(seller_id):
    seller = User.query.filter_by(id=seller_id, is_seller=True).first_or_404()
    products = Product.query.filter_by(seller_id=seller_id).all()
    return render_template('seller_profile.html', seller=seller, products=products)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'product')  # Default to product search
    
    if search_type == 'product':
        # Search in products
        products = Product.query.filter(
            Product.name.ilike(f'%{query}%') |
            Product.description.ilike(f'%{query}%')
        ).all()
        return render_template('search_results.html', 
                            products=products, 
                            query=query, 
                            search_type=search_type)
    else:
        # Search in seller units
        sellers = User.query.filter(
            User.is_seller == True
        ).filter(
            User.business_name.ilike(f'%{query}%') |
            User.username.ilike(f'%{query}%')
        ).all()
        
        # Get all products from matching sellers
        all_products = []
        for seller in sellers:
            seller_products = Product.query.filter_by(seller_id=seller.id).all()
            all_products.extend(seller_products)
            
        return render_template('search_results.html', 
                            products=all_products, 
                            sellers=sellers,
                            query=query, 
                            search_type=search_type)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Here you can add code to handle the contact form submission
        # For example, send an email or save to database
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('view_cart'))

    if request.method == 'POST':
        # Create new order
        order = Order(
            user_id=current_user.id,
            shipping_address=request.form.get('shipping_address'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),  # Get email from form
            payment_method=request.form.get('paymentMethod', 'cod'),
            total_amount=cart.total_amount
        )
        
        # Add order items
        for item in cart.items:
            order_item = OrderItem(
                order=order,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
        
        # Clear the cart
        for item in cart.items:
            db.session.delete(item)
        db.session.delete(cart)
        
        db.session.add(order)
        db.session.commit()

        # Send order confirmation email
        send_order_status_email(order)
        
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    return render_template('checkout.html', cart=cart)

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_confirmation.html', order=order)

@app.route('/order_details/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    # Ensure the seller owns at least one product in the order
    if not any(item.product.seller_id == current_user.id for item in order.items):
        abort(403)
    return render_template('order_details.html', order=order)

def send_order_status_email(order):
    try:
        print(f"\nAttempting to send email to: {order.email}")
        print(f"Using SMTP credentials - Username: {SMTP_USERNAME}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"KudumbaKart Order #{order.id} {order.status.title()}"
        msg['From'] = SMTP_USERNAME
        msg['To'] = order.email

        # Create HTML content
        html_content = render_template('email/order_status_update.html', order=order)
        msg.attach(MIMEText(html_content, 'html'))

        print("Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Enable debug output
        
        print("Starting TLS...")
        server.starttls()
        
        print("Attempting login...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        print("Sending message...")
        server.send_message(msg)
        
        print("Closing connection...")
        server.quit()
        
        print(f"Email sent successfully to {order.email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_seller:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    order = Order.query.get_or_404(order_id)
    if not any(item.product.seller_id == current_user.id for item in order.items):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    status = data.get('status')
    if status not in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    old_status = order.status
    order.status = status
    if status == 'delivered':
        order.payment_status = 'completed'
    
    db.session.commit()
    
    # Send email notification if status changed
    if old_status != status:
        send_order_status_email(order)
    
    return jsonify({'success': True})

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    if not current_user.is_seller:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    order = Order.query.get_or_404(order_id)
    # Ensure the seller owns at least one product in the order
    if not any(item.product.seller_id == current_user.id for item in order.items):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Delete order items first
        for item in order.items:
            db.session.delete(item)
        # Then delete the order
        db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('message', "Hello! How can I help you today?")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    """Handle incoming chat messages"""
    try:
        if isinstance(message, dict):
            message = message.get('message', '')
        response = bot.handle_message(message)
        emit('message', response)
    except Exception as e:
        print(f"Error in handle_message: {str(e)}")
        emit('message', "I apologize, but I encountered an error. Please try again.")

# Initialize database when app starts
@app.before_first_request
def initialize_database():
    db.create_all()

# Only run the application if this file is executed directly
if __name__ == '__main__':
    # Run the application locally
    socketio.run(app, debug=True)
