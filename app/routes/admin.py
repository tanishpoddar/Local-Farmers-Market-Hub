from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Product, Order, OrderItem, UserRole, OrderStatus
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin only.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.count()
    total_farmers = User.query.filter_by(role=UserRole.FARMER).count()
    total_buyers = User.query.filter_by(role=UserRole.BUYER).count()
    pending_farmers = User.query.filter_by(role=UserRole.FARMER, is_approved=False).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Sales statistics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_sales = Order.query.filter(
        Order.created_at >= thirty_days_ago,
        Order.status.in_([OrderStatus.COMPLETED, OrderStatus.READY])
    ).with_entities(func.sum(Order.total_price)).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_farmers=total_farmers,
                         total_buyers=total_buyers,
                         pending_farmers=pending_farmers,
                         total_products=total_products,
                         total_orders=total_orders,
                         recent_sales=recent_sales,
                         recent_orders=recent_orders)

@admin_bp.route('/admin/farmers')
@login_required
@admin_required
def manage_farmers():
    farmers = User.query.filter_by(role=UserRole.FARMER).order_by(User.created_at.desc()).all()
    return render_template('admin/manage_farmers.html', farmers=farmers)

@admin_bp.route('/admin/farmers/<int:farmer_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_farmer(farmer_id):
    farmer = User.query.get_or_404(farmer_id)
    
    if farmer.role != UserRole.FARMER:
        return jsonify({'success': False, 'message': 'User is not a farmer'}), 400
    
    farmer.is_approved = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Farmer approved successfully'})

@admin_bp.route('/admin/farmers/<int:farmer_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_farmer(farmer_id):
    farmer = User.query.get_or_404(farmer_id)
    
    if farmer.role != UserRole.FARMER:
        return jsonify({'success': False, 'message': 'User is not a farmer'}), 400
    
    # Delete farmer's products
    Product.query.filter_by(farmer_id=farmer.id).delete()
    
    # Delete farmer account
    db.session.delete(farmer)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Farmer rejected and removed'})

@admin_bp.route('/admin/orders')
@login_required
@admin_required
def manage_orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query
    
    if status_filter:
        query = query.filter_by(status=OrderStatus(status_filter))
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_orders.html', 
                         orders=orders,
                         status_filter=status_filter)

@admin_bp.route('/admin/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/admin/products')
@login_required
@admin_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Product.query.join(User)
    
    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%') |
            User.username.ilike(f'%{search}%')
        )
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_products.html',
                         products=products,
                         search=search)

@admin_bp.route('/admin/products/<int:product_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_product_availability(product_id):
    product = Product.query.get_or_404(product_id)
    
    product.available = not product.available
    db.session.commit()
    
    return jsonify({
        'success': True,
        'available': product.available,
        'message': f'Product {"activated" if product.available else "deactivated"}'
    })

@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=UserRole(role_filter))
    
    if search:
        query = query.filter(
            User.username.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%')
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_users.html',
                         users=users,
                         role_filter=role_filter,
                         search=search)

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's products if farmer
    if user.role == UserRole.FARMER:
        Product.query.filter_by(farmer_id=user.id).delete()
    
    # Delete user's orders
    Order.query.filter_by(buyer_id=user.id).delete()
    Order.query.filter_by(farmer_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@admin_bp.route('/admin/users/<int:user_id>/block', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot block your own account'}), 400
    user = User.query.get_or_404(user_id)
    user.is_blocked = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'User blocked successfully'})

@admin_bp.route('/admin/users/<int:user_id>/unblock', methods=['POST'])
@login_required
@admin_required
def unblock_user(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot unblock your own account'}), 400
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'User unblocked successfully'})

@admin_bp.route('/admin/reports')
@login_required
@admin_required
def reports():
    # Sales report
    sales_data = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_price).label('total_sales'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.status.in_([OrderStatus.COMPLETED, OrderStatus.READY])
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at).desc()
    ).limit(30).all()
    
    # Top products
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
    ).join(OrderItem).group_by(Product.id).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    
    # Top farmers
    top_farmers = db.session.query(
        User.username,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_price).label('total_revenue')
    ).join(Order, User.id == Order.farmer_id).group_by(User.id).order_by(
        func.sum(Order.total_price).desc()
    ).limit(10).all()
    
    return render_template('admin/reports.html',
                         sales_data=sales_data,
                         top_products=top_products,
                         top_farmers=top_farmers) 