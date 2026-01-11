#!/usr/bin/env python3
"""
Database seeding script for test data
Creates test users, products, and orders for demonstration
"""

from app import create_app, db
from app.models import User, UserRole, Product, Order, OrderItem, OrderStatus, DeliveryType
from datetime import datetime, timedelta
import random
import os

def seed_database():
    """Seed the database with test data"""
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
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create test users
        print("Creating test users...")
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@test.com',
            role=UserRole.ADMIN,
            is_approved=True,
            location='Admin Office',
            phone='555-0001'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Test buyer
        buyer = User(
            username='testbuyer',
            email='buyer@test.com',
            role=UserRole.BUYER,
            is_approved=True,
            location='Downtown City',
            phone='555-0002'
        )
        buyer.set_password('buyer123')
        db.session.add(buyer)
        
        # Test farmers
        farmers_data = [
            {
                'username': 'farmer1',
                'email': 'farmer1@test.com',
                'location': 'Green Valley Farm',
                'phone': '555-0003'
            },
            {
                'username': 'farmer2',
                'email': 'farmer2@test.com',
                'location': 'Sunny Acres Farm',
                'phone': '555-0004'
            },
            {
                'username': 'farmer3',
                'email': 'farmer3@test.com',
                'location': 'Organic Hills Farm',
                'phone': '555-0005'
            }
        ]
        
        farmers = []
        for farmer_data in farmers_data:
            farmer = User(
                username=farmer_data['username'],
                email=farmer_data['email'],
                role=UserRole.FARMER,
                is_approved=True,
                location=farmer_data['location'],
                phone=farmer_data['phone']
            )
            farmer.set_password('farmer123')
            farmers.append(farmer)
            db.session.add(farmer)
        
        # Commit users first
        db.session.commit()
        
        # Create test products
        print("Creating test products...")
        
        products_data = [
            # Farmer 1 products
            {
                'name': 'Fresh Tomatoes',
                'description': 'Juicy red tomatoes, perfect for salads and cooking',
                'price': 4.99,
                'quantity': 50,
                'unit': 'lb',
                'organic': True,
                'category': 'Vegetables',
                'farmer_id': farmers[0].id,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_fee': 2.50
            },
            {
                'name': 'Sweet Corn',
                'description': 'Fresh sweet corn, harvested daily',
                'price': 0.75,
                'quantity': 100,
                'unit': 'ear',
                'organic': False,
                'category': 'Vegetables',
                'farmer_id': farmers[0].id,
                'pickup_available': True,
                'delivery_available': False,
                'delivery_fee': 0.0
            },
            {
                'name': 'Farm Fresh Eggs',
                'description': 'Free-range chicken eggs from happy hens',
                'price': 6.50,
                'quantity': 30,
                'unit': 'dozen',
                'organic': True,
                'category': 'Dairy & Eggs',
                'farmer_id': farmers[0].id,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_fee': 1.50
            },
            
            # Farmer 2 products
            {
                'name': 'Organic Apples',
                'description': 'Crisp and sweet organic apples, various varieties',
                'price': 3.99,
                'quantity': 75,
                'unit': 'lb',
                'organic': True,
                'category': 'Fruits',
                'farmer_id': farmers[1].id,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_fee': 3.00
            },
            {
                'name': 'Fresh Strawberries',
                'description': 'Sweet, juicy strawberries picked this morning',
                'price': 5.99,
                'quantity': 25,
                'unit': 'pint',
                'organic': True,
                'category': 'Fruits',
                'farmer_id': farmers[1].id,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_fee': 2.00
            },
            {
                'name': 'Honey',
                'description': 'Pure wildflower honey from our beehives',
                'price': 12.99,
                'quantity': 20,
                'unit': 'jar',
                'organic': True,
                'category': 'Pantry',
                'farmer_id': farmers[1].id,
                'pickup_available': True,
                'delivery_available': False,
                'delivery_fee': 0.0
            },
            
            # Farmer 3 products
            {
                'name': 'Organic Lettuce',
                'description': 'Fresh organic lettuce, perfect for salads',
                'price': 2.99,
                'quantity': 40,
                'unit': 'head',
                'organic': True,
                'category': 'Vegetables',
                'farmer_id': farmers[2].id,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_fee': 1.50
            },
            {
                'name': 'Bell Peppers',
                'description': 'Colorful bell peppers - red, yellow, and green',
                'price': 1.99,
                'quantity': 60,
                'unit': 'each',
                'organic': False,
                'category': 'Vegetables',
                'farmer_id': farmers[2].id,
                'pickup_available': True,
                'delivery_available': True,
                'delivery_fee': 2.00
            },
            {
                'name': 'Fresh Herbs Bundle',
                'description': 'Mixed fresh herbs: basil, parsley, cilantro',
                'price': 4.50,
                'quantity': 15,
                'unit': 'bundle',
                'organic': True,
                'category': 'Herbs',
                'farmer_id': farmers[2].id,
                'pickup_available': True,
                'delivery_available': False,
                'delivery_fee': 0.0
            }
        ]
        
        products = []
        for product_data in products_data:
            product = Product(**product_data)
            products.append(product)
            db.session.add(product)
        
        # Commit products
        db.session.commit()
        
        # Create some test orders
        print("Creating test orders...")
        
        # Order 1: Completed order
        order1 = Order(
            buyer_id=buyer.id,
            farmer_id=farmers[0].id,
            status=OrderStatus.COMPLETED,
            delivery_type=DeliveryType.PICKUP,
            delivery_address='',
            delivery_fee=0.0,
            notes='Please have ready by 3 PM',
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(order1)
        db.session.commit()
        
        # Order items for order 1
        order1_item1 = OrderItem(
            order_id=order1.id,
            product_id=products[0].id,  # Tomatoes
            quantity=2,
            price=products[0].price
        )
        order1_item2 = OrderItem(
            order_id=order1.id,
            product_id=products[2].id,  # Eggs
            quantity=1,
            price=products[2].price
        )
        db.session.add(order1_item1)
        db.session.add(order1_item2)
        
        # Order 2: Pending order
        order2 = Order(
            buyer_id=buyer.id,
            farmer_id=farmers[1].id,
            status=OrderStatus.PENDING,
            delivery_type=DeliveryType.DELIVERY,
            delivery_address='123 Main St, Downtown City',
            delivery_fee=3.0,
            notes='Ring doorbell twice',
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(order2)
        db.session.commit()
        
        # Order items for order 2
        order2_item1 = OrderItem(
            order_id=order2.id,
            product_id=products[3].id,  # Apples
            quantity=3,
            price=products[3].price
        )
        order2_item2 = OrderItem(
            order_id=order2.id,
            product_id=products[4].id,  # Strawberries
            quantity=2,
            price=products[4].price
        )
        db.session.add(order2_item1)
        db.session.add(order2_item2)
        
        # Calculate totals
        order1.calculate_total()
        order2.calculate_total()
        
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print("\n🔑 Test Credentials:")
        print("=" * 40)
        print("👤 Admin:")
        print("   Email: admin@test.com")
        print("   Password: admin123")
        print("\n🛒 Buyer:")
        print("   Email: buyer@test.com")
        print("   Password: buyer123")
        print("\n🌾 Farmers:")
        print("   Email: farmer1@test.com")
        print("   Password: farmer123")
        print("   Email: farmer2@test.com")
        print("   Password: farmer123")
        print("   Email: farmer3@test.com")
        print("   Password: farmer123")
        print("=" * 40)
        
        print(f"\n📊 Created:")
        print(f"   • {len(farmers) + 2} users (1 admin, 1 buyer, {len(farmers)} farmers)")
        print(f"   • {len(products)} products")
        print(f"   • 2 sample orders")

if __name__ == '__main__':
    seed_database()