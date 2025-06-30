from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, template, **kwargs):
    """Send email using template"""
    try:
        msg = Message(subject, recipients=recipients)
        msg.html = render_template(f'emails/{template}.html', **kwargs)
        
        # Send email asynchronously
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_order_confirmation(order):
    """Send order confirmation to buyer"""
    subject = f"Order Confirmation - Order #{order.id}"
    recipients = [order.buyer.email]
    
    return send_email(
        subject=subject,
        recipients=recipients,
        template='order_confirmation',
        order=order
    )

def send_order_notification(order):
    """Send order notification to farmer"""
    subject = f"New Order Received - Order #{order.id}"
    recipients = [order.farmer.email]
    
    return send_email(
        subject=subject,
        recipients=recipients,
        template='order_notification',
        order=order
    )

def send_order_status_update(order):
    """Send order status update to buyer"""
    subject = f"Order Status Update - Order #{order.id}"
    recipients = [order.buyer.email]
    
    return send_email(
        subject=subject,
        recipients=recipients,
        template='order_status_update',
        order=order
    )

def send_farmer_approval_notification(user):
    """Send approval notification to farmer"""
    subject = "Your Farmer Account Has Been Approved!"
    recipients = [user.email]
    
    return send_email(
        subject=subject,
        recipients=recipients,
        template='farmer_approval',
        user=user
    )

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = "Welcome to Local Farmer's Market Hub!"
    recipients = [user.email]
    
    return send_email(
        subject=subject,
        recipients=recipients,
        template='welcome',
        user=user
    ) 