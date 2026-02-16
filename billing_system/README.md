# Billing System

A Django-based billing system for retail stores with inventory management, denomination tracking, and automated invoice generation.

## Features

- **Product Management**: Add and manage products with stock, price, and tax information
- **Dynamic Billing**: Create bills with multiple items
- **Denomination Tracking**: Track available denominations in the shop
- **Smart Change Calculation**: Automatically calculates the optimal denomination breakdown for customer balance
- **Email Invoices**: Automatically sends invoices to customers via email
- **Purchase History**: View all previous purchases by customer email
- **Stock Management**: Automatically updates inventory when bills are generated
- **Admin Interface**: Django admin panel for easy product and denomination management

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (for Admin Access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 4. Seed Initial Data

You can add products and denominations through the admin panel or use Django shell:

```bash
python manage.py shell
```

Then run:

```python
from billing.models import Product, ShopDenomination

# Add sample products
Product.objects.create(
    product_id="P001",
    name="Laptop",
    available_stocks=10,
    price=50000.00,
    tax_percentage=18.00
)

Product.objects.create(
    product_id="P002",
    name="Mouse",
    available_stocks=50,
    price=500.00,
    tax_percentage=12.00
)

Product.objects.create(
    product_id="P003",
    name="Keyboard",
    available_stocks=30,
    price=1500.00,
    tax_percentage=12.00
)

# Add denominations available in shop
for value in [500, 50, 20, 10, 5, 2, 1]:
    ShopDenomination.objects.create(value=value, count=100)
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Creating a Bill

1. Navigate to `http://127.0.0.1:8000/`
2. Enter customer email
3. Add products using Product ID and quantity
4. Click "Add New" to add more products
5. Enter the count of denominations received from the customer
6. Enter the total amount paid by the customer
7. Click "Generate Bill"

The system will:
- Validate product availability
- Calculate taxes and totals
- Determine the optimal denomination breakdown for balance
- Update inventory
- Update shop denominations
- Send an invoice email
- Display the detailed bill

### Viewing Customer Purchase History

1. Navigate to `http://127.0.0.1:8000/customer-purchases/`
2. Enter customer email
3. Click "Search"
4. Click on any bill to expand and view items purchased

### Managing Products and Denominations

1. Access the admin panel at `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials
3. Navigate to:
   - **Products**: Add, edit, or delete products
   - **Shop Denominations**: View and manage available cash denominations

## Database Schema

### Product
- `product_id`: Unique identifier for the product
- `name`: Product name
- `available_stocks`: Current stock count
- `price`: Unit price (without tax)
- `tax_percentage`: Tax percentage applicable

### Bill
- `customer_email`: Customer's email address
- `total_price_without_tax`: Sum of all items before tax
- `total_tax`: Total tax amount
- `net_price`: Total amount (with tax)
- `rounded_net_price`: Rounded up total
- `amount_paid`: Amount paid by customer
- `balance`: Change to be returned
- `created_at`: Timestamp of bill creation

### BillItem
- `bill`: Foreign key to Bill
- `product`: Foreign key to Product
- `quantity`: Quantity purchased
- `unit_price`: Price per unit at time of purchase
- `tax_percentage`: Tax percentage at time of purchase
- `tax_amount`: Calculated tax amount
- `total_price`: Total for this line item

### ShopDenomination
- `value`: Denomination value (500, 50, 20, 10, 5, 2, 1)
- `count`: Number of notes/coins available

### BalanceDenomination
- `bill`: Foreign key to Bill
- `value`: Denomination value
- `count`: Number of notes/coins returned

## Email Configuration

By default, the system uses Django's console email backend (emails are printed to console).

For production, update `billing_system/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

## Assumptions

1. **Rounding Logic**: The net price is always rounded up to the nearest integer (ceiling function)
2. **Denomination Algorithm**: Uses a greedy algorithm to minimize the number of notes/coins for balance
3. **Stock Updates**: Stock is immediately deducted when a bill is generated (no separate checkout process)
4. **Email Delivery**: Emails are sent asynchronously in the background (in production, consider using Celery)
5. **Currency**: All amounts are in Indian Rupees (₹)
6. **Concurrent Transactions**: Uses database transactions to prevent race conditions on stock updates
7. **Insufficient Balance**: If the shop doesn't have enough denominations to return the exact balance, the transaction is rolled back

## Testing

### Test Scenario 1: Simple Purchase

1. Add denominations: 500:10, 50:20, 20:30, 10:40, 5:50, 2:60, 1:70
2. Create bill with:
   - Customer: test@example.com
   - Product P001 (₹50,000, 18% tax), Quantity: 1
   - Amount paid: ₹60,000
3. Expected result:
   - Net price: ₹59,000
   - Balance: ₹1,000
   - Balance denominations: 500:2

### Test Scenario 2: Multiple Items

1. Create bill with:
   - Customer: test@example.com
   - Product P002 (₹500, 12% tax), Quantity: 3
   - Product P003 (₹1,500, 12% tax), Quantity: 2
   - Amount paid: ₹5,000
2. Expected result:
   - Subtotal: ₹4,500
   - Tax: ₹540
   - Net price: ₹5,040
   - Balance: -₹40 (ERROR: Insufficient payment)

### Test Scenario 3: Insufficient Stock

1. Create bill with:
   - Product P001, Quantity: 100 (only 10 in stock)
2. Expected result: Error message about insufficient stock

## Production Considerations

1. **Security**: Change `SECRET_KEY` in settings.py
2. **Database**: Use PostgreSQL or MySQL instead of SQLite
3. **Static Files**: Configure proper static file serving
4. **Email**: Set up proper SMTP configuration
5. **Background Tasks**: Use Celery for email sending and other async tasks
6. **Error Logging**: Implement proper logging and monitoring
7. **Backup**: Regular database backups
8. **HTTPS**: Enable SSL/TLS in production

## Project Structure

```
billing_system/
├── billing/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── billing_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── base.html
│   └── billing/
│       ├── index.html
│       ├── bill_detail.html
│       └── customer_purchases.html
├── manage.py
├── requirements.txt
└── README.md
```

## Support

For issues or questions, please refer to the Django documentation at https://docs.djangoproject.com/
