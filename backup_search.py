# Backup of original search implementation
from app import app, db
from models import Product

@app.route('/search')
def search():
    query = request.args.get('q', '')
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%') |
        Product.description.ilike(f'%{query}%')
    ).all()
    return render_template('search_results.html', products=products, query=query)
