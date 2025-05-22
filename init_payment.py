def init_payment_system(app):
    # Import the payment routes
    from routes.payment import init_payment_routes
    
    # Initialize the payment routes
    init_payment_routes(app)
    
    return app
