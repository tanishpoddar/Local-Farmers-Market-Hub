from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.models import Product, User, UserRole
from app import db
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured products (available products from approved farmers)
    featured_products = Product.query.join(User).filter(
        Product.available == True,
        User.is_approved == True,
        User.role == UserRole.FARMER
    ).limit(8).all()
    
    # Get categories
    categories = db.session.query(Product.category).distinct().filter(
        Product.category.isnot(None)
    ).all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('main/index.html', 
                         featured_products=featured_products,
                         categories=categories)

@main_bp.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Build query
    query = Product.query.join(User).filter(
        Product.available == True,
        User.is_approved == True,
        User.role == UserRole.FARMER
    )
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                User.location.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Pagination
    products = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get categories for filter
    categories = db.session.query(Product.category).distinct().filter(
        Product.category.isnot(None)
    ).all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('main/products.html',
                         products=products,
                         categories=categories,
                         search=search,
                         category=category,
                         min_price=min_price,
                         max_price=max_price)

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if farmer is approved
    if not product.farmer.is_approved or product.farmer.role != UserRole.FARMER:
        flash('This product is not available.', 'error')
        return redirect(url_for('main.products'))
    
    # Get related products from same farmer
    related_products = Product.query.filter(
        Product.farmer_id == product.farmer_id,
        Product.id != product.id,
        Product.available == True
    ).limit(4).all()
    
    return render_template('main/product_detail.html',
                         product=product,
                         related_products=related_products)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.products'))
    
    products = Product.query.join(User).filter(
        Product.available == True,
        User.is_approved == True,
        User.role == UserRole.FARMER,
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Product.category.ilike(f'%{query}%'),
            User.location.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template('main/search_results.html',
                         products=products,
                         query=query)

@main_bp.route('/api/products')
def api_products():
    """API endpoint for AJAX product loading"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Product.query.join(User).filter(
        Product.available == True,
        User.is_approved == True,
        User.role == UserRole.FARMER
    )
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'image': p.image,
            'farmer_name': p.farmer.username,
            'location': p.farmer.location
        } for p in products.items],
        'has_next': products.has_next,
        'has_prev': products.has_prev,
        'page': page
    })

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/become-farmer', methods=['GET', 'POST'])
def become_farmer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        message = request.form.get('message')
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with this email already exists.', 'error')
            return render_template('become_farmer.html')
        # Create new farmer user (pending approval)
        new_user = User()
        new_user.username = name
        new_user.email = email
        new_user.phone = phone
        new_user.location = address
        new_user.role = UserRole.FARMER
        new_user.is_approved = False
        new_user.set_password('changeme123')
        db.session.add(new_user)
        db.session.commit()
        flash('Your application has been submitted! We will contact you soon.', 'success')
        return redirect(url_for('main.become_farmer'))
    return render_template('become_farmer.html') 