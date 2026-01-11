#!/usr/bin/env python3
"""
Deployment script for Render
This script initializes the database and creates test users for demonstration.
"""

from app import create_app, db
from app.models import User, UserRole, Product
import os

def deploy():
    """Run deployment tasks."""
    app = create_app()
    
    with app.app_context():
        # Ensure database directory exists
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                print(f"Ensured database directory exists: {db_dir}")
        
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@test.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email=admin_email,
                role=UserRole.ADMIN,
                is_approved=True,
                location='Admin Office',
                phone='555-0001'
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            print(f"Admin user created with email: {admin_email}")
        else:
            print("Admin user already exists")
        
        # Create test buyer if it doesn't exist
        test_buyer = User.query.filter_by(email='buyer@test.com').first()
        if not test_buyer:
            test_buyer = User(
                username='testbuyer',
                email='buyer@test.com',
                role=UserRole.BUYER,
                is_approved=True,
                location='Downtown City',
                phone='555-0002'
            )
            test_buyer.set_password('buyer123')
            db.session.add(test_buyer)
            print("Test buyer created: buyer@test.com")
        
        # Create test farmer if it doesn't exist
        test_farmer = User.query.filter_by(email='farmer1@test.com').first()
        if not test_farmer:
            test_farmer = User(
                username='farmer1',
                email='farmer1@test.com',
                role=UserRole.FARMER,
                is_approved=True,
                location='Green Valley Farm',
                phone='555-0003'
            )
            test_farmer.set_password('farmer123')
            db.session.add(test_farmer)
            print("Test farmer created: farmer1@test.com")
        
        # Add a sample product if farmer exists and no products exist
        if test_farmer and Product.query.count() == 0:
            sample_product = Product(
                name='Fresh Tomatoes',
                description='Juicy red tomatoes, perfect for salads and cooking',
                price=4.99,
                quantity=50,
                unit='lb',
                organic=True,
                category='Vegetables',
                farmer_id=test_farmer.id,
                pickup_available=True,
                delivery_available=True,
                delivery_fee=2.50
            )
            db.session.add(sample_product)
            print("Sample product created")
        
        db.session.commit()
        
        print("\n🔑 Test Credentials Available:")
        print("👤 Admin: admin@test.com / admin123")
        print("🛒 Buyer: buyer@test.com / buyer123")
        print("🌾 Farmer: farmer1@test.com / farmer123")
        print("\n✅ Deployment completed successfully!")

if __name__ == '__main__':
    deploy()