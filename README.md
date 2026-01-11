# Local Farmer's Market Hub

A modern web application connecting local farmers with buyers and empowering admins to manage the marketplace. Built with Flask, SQLAlchemy, Flask-Login, Tailwind CSS, and Flask-Mail.

## Features

### For Buyers
- Browse and search fresh local products
- Add items to cart and checkout
- Track your orders and view order history

### For Farmers
- Apply to become a farmer via a dedicated form
- Manage your product listings (add, edit, delete)
- View and update order statuses for your products

### For Admins
- Dashboard with marketplace stats
- Approve/reject farmer applications
- Manage all users (block/unblock/delete)
- Oversee all products and orders
- View sales and analytics reports

### General
- Responsive, mobile-friendly UI (Tailwind CSS)
- Email notifications for key actions
- Secure authentication and role-based access
- Custom About Us and Become a Farmer pages
- Favicon and branding support

## Installation

### Prerequisites
- Python 3.8+
- pip

### Steps
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Farmers
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Activate:
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **(Optional) Configure environment variables:**
   Create a `.env` file for secrets and email config:
   ```env
   SECRET_KEY=your-secret-key
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```
5. **Run the app:**
   ```bash
   python run.py
   ```
   Visit [http://localhost:5000](http://localhost:5000)

6. **(Optional) Seed test data:**
   ```bash
   python seed_data.py
   ```
   This creates test users, products, and orders for easy testing.

## Test Credentials

After running the seed script, you can use these test accounts:

- **Admin**: admin@test.com / admin123
- **Buyer**: buyer@test.com / buyer123  
- **Farmers**: farmer1@test.com / farmer123 (also farmer2, farmer3)

The login page includes quick-fill buttons for easy testing.

## Usage

- **Sign up** as a buyer or use the Become a Farmer form to apply as a farmer.
- **Farmers**: Wait for admin approval, then manage your products and orders.
- **Buyers**: Browse, search, add to cart, and place orders.
- **Admins**: Access the admin dashboard to manage users, products, orders, and reports.

## Credits

Made with ❤️ by Tanish Poddar

## License

MIT License. See `LICENSE` for details. 