# 🌾 Local Farmer's Market Hub

> **Live Demo:** [https://local-farmers-market-hub.onrender.com](https://local-farmers-market-hub.onrender.com)

A modern web application connecting local farmers with buyers, featuring a comprehensive admin panel for marketplace management. Built with Flask, SQLAlchemy, and Tailwind CSS.

## ✨ Features

### 🛒 **For Buyers**
- Browse and search fresh local products by category, price, and location
- Add items to cart with real-time inventory checking
- Secure checkout with delivery options
- Order tracking and history management
- User profile and account management

### 🌱 **For Farmers**
- Apply to become a farmer through dedicated application form
- Comprehensive product management (add, edit, delete, inventory tracking)
- Order management with status updates
- Sales analytics and reporting
- Profile management with farm location details

### 👨‍💼 **For Admins**
- Comprehensive dashboard with marketplace statistics
- User management (approve farmers, block/unblock users)
- Product oversight and moderation
- Order monitoring across all farmers
- Sales reports and analytics
- Email notification system management

### 🎨 **General Features**
- Responsive, mobile-first design with Tailwind CSS
- Real-time cart updates and notifications
- Email notifications for orders and status changes
- Secure authentication with role-based access control
- Search and filtering capabilities
- Image upload for products
- Organic certification badges

## 🧪 **Try It Out**

Visit the live demo and test with these accounts:

| Role | Email | Password | What You Can Do |
|------|-------|----------|-----------------|
| 👤 **Admin** | admin@test.com | admin123 | Manage users, products, orders, view analytics |
| 🛒 **Buyer** | buyer@test.com | buyer123 | Browse products, add to cart, place orders |
| 🌾 **Farmer** | farmer1@test.com | farmer123 | Manage products, fulfill orders, track sales |

*The login page includes quick-fill buttons for easy testing!*

## 🛠️ **Tech Stack**

- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-Mail
- **Frontend:** HTML5, Tailwind CSS, JavaScript
- **Database:** SQLite (production-ready for small-medium scale)
- **Deployment:** Render with persistent storage
- **Authentication:** Secure password hashing with Werkzeug
- **Email:** SMTP integration for notifications

## 🚀 **Local Development**

### Prerequisites
- Python 3.8+
- pip

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Local-Farmers-Market-Hub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed test data (optional)
python seed_data.py

# Run the application
python run.py
```

Visit [http://localhost:5000](http://localhost:5000)

## 📱 **Screenshots & Demo**

### 🏠 Homepage
- Featured products from approved farmers
- Category-based browsing
- Search functionality

### 🛒 Shopping Experience
- Product detail pages with farmer information
- Real-time cart management
- Secure checkout process

### 📊 Admin Dashboard
- User management and farmer approvals
- Product oversight and inventory monitoring
- Order tracking and analytics

### 🌾 Farmer Portal
- Product management interface
- Order fulfillment workflow
- Sales tracking and reporting

## 🔧 **Key Features Implemented**

- **Role-Based Access Control:** Different interfaces for buyers, farmers, and admins
- **Real-Time Inventory:** Automatic stock updates and availability checking
- **Email Notifications:** Order confirmations and status updates
- **Responsive Design:** Works seamlessly on desktop, tablet, and mobile
- **Search & Filtering:** Advanced product discovery with multiple filters
- **Admin Restrictions:** Admins cannot access buyer functionality (cart, checkout)
- **Security:** CSRF protection, secure password hashing, input validation

## 🎯 **Use Cases**

- **Local Farmers Markets:** Digital presence for traditional markets
- **Community Supported Agriculture (CSA):** Direct farmer-to-consumer sales
- **Organic Food Cooperatives:** Specialized organic product marketplaces
- **Farm-to-Table Restaurants:** Direct sourcing from local farmers
- **Educational Projects:** Learning platform for e-commerce development

## 🤝 **Contributing**

This project demonstrates modern web development practices including:
- MVC architecture with Flask blueprints
- Database relationships and migrations
- User authentication and authorization
- Email integration and notifications
- Responsive web design
- Production deployment strategies

## 📄 **License**

MIT License - feel free to use this project for learning or as a foundation for your own marketplace application.

---

**Made with ❤️ by Tanish Poddar**

*Supporting local farmers and sustainable agriculture through technology* 🌱