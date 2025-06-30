from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Product, UserRole
from app import db
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

products_bp = Blueprint('products', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Save file
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Resize image for web
        with Image.open(filepath) as img:
            img.thumbnail((800, 800))  # Max dimensions
            img.save(filepath, quality=85, optimize=True)
        
        return f"uploads/{unique_filename}"
    return None

@products_bp.route('/farmer/products')
@login_required
def farmer_products():
    if not current_user.is_farmer():
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('main.index'))
    
    products = Product.query.filter_by(farmer_id=current_user.id).order_by(Product.created_at.desc()).all()
    return render_template('products/farmer_products.html', products=products)

@products_bp.route('/farmer/products/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if not current_user.is_farmer():
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('main.index'))
    
    if not current_user.is_approved:
        flash('Your account needs to be approved before you can add products.', 'warning')
        return redirect(url_for('products.farmer_products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category = request.form.get('category')
        unit = request.form.get('unit')
        organic = 'organic' in request.form
        
        # Validation
        if not all([name, price, stock, category, unit]):
            flash('Please fill in all required fields.', 'error')
            return render_template('products/new_product.html')
        
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash('Please enter valid numbers for price and stock.', 'error')
            return render_template('products/new_product.html')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_path = save_image(file)
        
        # Create product
        product = Product(
            name=name,
            description=description,
            price=price,
            quantity=stock,
            unit=unit,
            organic=organic,
            category=category,
            farmer_id=current_user.id,
            image=image_path,
            available=True
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('products.farmer_products'))
    
    return render_template('products/new_product.html')

@products_bp.route('/farmer/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_farmer():
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(product_id)
    
    # Check ownership
    if product.farmer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('products.farmer_products'))
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description', '')
        product.price = float(request.form.get('price'))
        product.quantity = int(request.form.get('stock'))
        product.category = request.form.get('category')
        product.unit = request.form.get('unit')
        product.organic = 'organic' in request.form
        product.available = True
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_path = save_image(file)
                if image_path:
                    # Delete old image if exists
                    if product.image:
                        old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image.replace('uploads/', ''))
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    product.image = image_path
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.farmer_products'))
    
    return render_template('products/edit_product.html', product=product)

@products_bp.route('/farmer/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_farmer():
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(product_id)
    
    # Check ownership
    if product.farmer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('products.farmer_products'))
    
    # Delete image if exists
    if product.image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image.replace('uploads/', ''))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.farmer_products'))

@products_bp.route('/farmer/products/<int:product_id>/toggle', methods=['POST'])
@login_required
def toggle_product(product_id):
    if not current_user.is_farmer():
        return {'success': False, 'message': 'Access denied'}, 403
    
    product = Product.query.get_or_404(product_id)
    
    if product.farmer_id != current_user.id:
        return {'success': False, 'message': 'Access denied'}, 403
    
    product.available = not product.available
    db.session.commit()
    
    return {'success': True, 'available': product.available} 