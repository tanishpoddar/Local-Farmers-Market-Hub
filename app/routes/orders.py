from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app.models import Product, Order, OrderItem, UserRole, OrderStatus, DeliveryType
from app import db
from app.email_utils import send_order_confirmation, send_order_notification
import json

orders_bp = Blueprint('orders', __name__)

def get_cart():
    """Get cart from session"""
    return session.get('cart', {})

def save_cart(cart):
    """Save cart to session"""
    session['cart'] = cart

def clear_cart():
    """Clear cart from session"""
    session.pop('cart', None)

@orders_bp.route('/cart')
def cart():
    cart_data = get_cart()
    cart_items = []
    total = 0
    
    for product_id, quantity in cart_data.items():
        product = Product.query.get(product_id)
        if product and product.available and product.quantity >= quantity:
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    return render_template('orders/cart.html', cart_items=cart_items, total=total)

@orders_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please log in to add items to cart'})
    
    product = Product.query.get_or_404(product_id)
    
    if not product.available:
        return jsonify({'success': False, 'message': 'Product is not available'})
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > product.quantity:
        return jsonify({'success': False, 'message': f'Only {product.quantity} available'})
    
    cart = get_cart()
    
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    
    # Check if total quantity doesn't exceed available
    if cart[str(product_id)] > product.quantity:
        cart[str(product_id)] = product.quantity
    
    save_cart(cart)
    
    return jsonify({
        'success': True, 
        'message': 'Added to cart',
        'cart_count': sum(cart.values())
    })

@orders_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 0))
    
    cart = get_cart()
    
    if quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        if quantity > product.quantity:
            return jsonify({'success': False, 'message': f'Only {product.quantity} available'})
        cart[str(product_id)] = quantity
    
    save_cart(cart)
    
    return jsonify({
        'success': True,
        'cart_count': sum(cart.values())
    })

@orders_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    
    return jsonify({
        'success': True,
        'cart_count': sum(cart.values())
    })

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_data = get_cart()
    # Always calculate cart_items and total at the start
    cart_items = []
    total = 0
    for product_id, quantity in cart_data.items():
        product = Product.query.get(product_id)
        if product and product.available and product.quantity >= quantity:
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    if not cart_data:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('orders.cart'))
    
    # Group products by farmer (for order creation)
    farmer_orders = {}
    for product_id, quantity in cart_data.items():
        product = Product.query.get(product_id)
        if product and product.available and product.quantity >= quantity:
            if product.farmer_id not in farmer_orders:
                farmer_orders[product.farmer_id] = []
            farmer_orders[product.farmer_id].append({
                'product': product,
                'quantity': quantity
            })
    
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address', '')
        shipping_city = request.form.get('shipping_city', '')
        shipping_state = request.form.get('shipping_state', '')
        shipping_zip = request.form.get('shipping_zip', '')
        notes = request.form.get('notes', '')
        
        if not all([shipping_address, shipping_city, shipping_state, shipping_zip]):
            flash('Please provide complete shipping information.', 'error')
            return render_template('orders/checkout.html', cart_items=cart_items, total=total)
        
        # Create orders for each farmer
        orders_created = []
        for farmer_id, items in farmer_orders.items():
            order = Order(
                buyer_id=current_user.id,
                farmer_id=farmer_id,
                delivery_type=DeliveryType.DELIVERY,  # Default to delivery
                delivery_address=f"{shipping_address}, {shipping_city}, {shipping_state} {shipping_zip}",
                notes=notes
            )
            
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add order items
            for item_data in items:
                product = item_data['product']
                quantity = item_data['quantity']
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=product.price
                )
                db.session.add(order_item)
                
                # Update product quantity
                product.quantity -= quantity
                if product.quantity <= 0:
                    product.available = False
            
            order.calculate_total()
            orders_created.append(order)
        
        db.session.commit()
        
        # Clear cart
        clear_cart()
        
        # Send email notifications
        for order in orders_created:
            try:
                send_order_confirmation(order)
                send_order_notification(order)
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        flash('Orders placed successfully! You will receive email confirmations.', 'success')
        return redirect(url_for('orders.my_orders'))
    
    return render_template('orders/checkout.html', cart_items=cart_items, total=total)

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    if current_user.role == UserRole.BUYER:
        orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
    elif current_user.role == UserRole.FARMER:
        orders = Order.query.filter_by(farmer_id=current_user.id).order_by(Order.created_at.desc()).all()
    else:
        orders = []
    
    return render_template('orders/my_orders.html', orders=orders)

@orders_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check access
    if current_user.role == UserRole.BUYER and order.buyer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('orders.my_orders'))
    
    if current_user.role == UserRole.FARMER and order.farmer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('orders.my_orders'))
    
    return render_template('orders/order_detail.html', order=order)

@orders_bp.route('/order/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    print(f"User {current_user.id} ({current_user.role}) attempting to update order {order_id}")
    if current_user.role != UserRole.FARMER:
        print("Access denied: not a farmer")
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    order = Order.query.get_or_404(order_id)

    if order.farmer_id != current_user.id:
        print("Access denied: not the owner farmer")
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    new_status = request.form.get('status')
    print(f"Requested new status: {new_status}")

    if new_status not in [status.value for status in OrderStatus]:
        print("Invalid status value")
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    order.status = OrderStatus(new_status)
    db.session.commit()
    print(f"Order {order_id} status updated to {order.status.value}")

    # Send email notification to buyer
    try:
        send_order_notification(order)
    except Exception as e:
        print(f"Email sending failed: {e}")

    return jsonify({'success': True, 'status': order.status.value})

@orders_bp.route('/api/cart-count')
def cart_count():
    if not current_user.is_authenticated:
        return jsonify({'count': 0})
    
    cart = get_cart()
    return jsonify({'count': sum(cart.values())}) 