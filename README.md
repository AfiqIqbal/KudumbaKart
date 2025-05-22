# KudumbaKart

A digital marketplace connecting Kudumbashree units in Kerala with a broader customer base. This e-commerce platform enables women's self-help groups to sell their traditional and handmade products online.

## Features

### User Management
- User Registration and Authentication
- Separate buyer and seller roles
- Seller verification system
- Profile management

### Seller Dashboard
- Complete business overview with analytics
- Product management (add, edit, delete)
- Order tracking and fulfillment
- Sales reporting

### Product Features
- Detailed product listings with optimized images
- Category-based browsing
- Advanced search functionality
- Product reviews and ratings

### Shopping Experience
- Responsive, modern UI
- Dynamic shopping cart
- Secure checkout process
- Order tracking
- Email notifications

### Support Features
- Integrated chatbot
- Contact form
- Help documentation

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5.1.3, JavaScript
- **Authentication**: Flask-Login
- **Additional**: Flask-Migrate, Flask-WTF, Flask-SocketIO
- **AI Integration**: LangChain, FAISS for vector search

## Setup Instructions

1. Install Python 3.8 or higher
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
5. Initialize the database:
   ```
   python init_db.py
   ```
6. Run the application:
   ```
   python run.py
   ```
7. Access the application at `http://localhost:5000`

## Project Structure

```
KudumbaKart/
├── app.py                # Main application file
├── models.py             # Database models
├── run.py                # Application runner
├── chatbot.py            # Chatbot integration
├── requirements.txt      # Python dependencies
├── static/               # Static files (CSS, JS, images)
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Image assets
├── templates/            # HTML templates
│   └── email/            # Email templates
├── utils/                # Utility scripts
└── instance/             # Instance-specific files (database)
```

## Contributors

- Afiq Iqbal K
- Nandhana K P
- Akshara Nair

## Future Enhancements

- Payment gateway integration
- Mobile application development
- Enhanced analytics and reporting
- Multi-language support
- Wishlist functionality
- Subscription-based delivery options
