from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Cart, Order, OrderItem, Payment
import uuid

def init_payment_routes(app):
    @app.route('/checkout')
    @login_required
    def checkout():
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart or not cart.items:
            flash('Your cart is empty', 'warning')
            return redirect(url_for('view_cart'))
        return render_template('checkout.html', cart=cart)

    @app.route('/process-payment', methods=['POST'])
    @login_required
    def process_payment():
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart or not cart.items:
            flash('Your cart is empty', 'warning')
            return redirect(url_for('view_cart'))

        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=cart.get_total() + 50,  # Adding shipping cost
            shipping_address=request.form.get('address'),
            shipping_city=request.form.get('city'),
            shipping_state=request.form.get('state'),
            shipping_pincode=request.form.get('pincode'),
            contact_number=request.form.get('phone'),
            status='pending'
        )
        db.session.add(order)

        # Create order items
        for cart_item in cart.items:
            order_item = OrderItem(
                order=order,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)

        # Create payment record
        payment = Payment(
            order=order,
            amount=order.total_amount,
            payment_method=request.form.get('paymentMethod'),
            transaction_id=f'TXN_{uuid.uuid4().hex[:12].upper()}',
            status='pending'
        )
        db.session.add(payment)

        # Clear the cart
        for item in cart.items:
            db.session.delete(item)
        db.session.delete(cart)

        try:
            db.session.commit()
            return render_template('payment_processing.html', order=order, payment=payment)
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your order', 'error')
            return redirect(url_for('checkout'))

    @app.route('/payment-success')
    @login_required
    def payment_success():
        # Get the latest order and payment
        order = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).first()
        if not order:
            return redirect(url_for('index'))
        
        payment = Payment.query.filter_by(order_id=order.id).first()
        if payment:
            payment.status = 'completed'
            order.status = 'confirmed'
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
        return render_template('payment_success.html', order=order, payment=payment)

    @app.route('/view-orders')
    @login_required
    def view_orders():
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template('orders.html', orders=orders)
