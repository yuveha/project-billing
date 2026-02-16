#!/usr/bin/env python
"""
Quick setup script to initialize the billing system with sample data
Run this after: python manage.py migrate
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_system.settings')
django.setup()

from billing.models import Product, ShopDenomination

def setup():
    print("Setting up Billing System...")
    
    # Add sample products
    products = [
        {
            'product_id': 'P001',
            'name': 'Laptop Dell Inspiron',
            'available_stocks': 10,
            'price': 50000.00,
            'tax_percentage': 18.00
        },
        {
            'product_id': 'P002',
            'name': 'Wireless Mouse',
            'available_stocks': 50,
            'price': 500.00,
            'tax_percentage': 12.00
        },
        {
            'product_id': 'P003',
            'name': 'Mechanical Keyboard',
            'available_stocks': 30,
            'price': 1500.00,
            'tax_percentage': 12.00
        },
        {
            'product_id': 'P004',
            'name': 'USB Cable',
            'available_stocks': 100,
            'price': 150.00,
            'tax_percentage': 12.00
        },
        {
            'product_id': 'P005',
            'name': 'Monitor 24 inch',
            'available_stocks': 15,
            'price': 12000.00,
            'tax_percentage': 18.00
        }
    ]
    
    print("\nAdding products...")
    for product_data in products:
        product, created = Product.objects.get_or_create(
            product_id=product_data['product_id'],
            defaults=product_data
        )
        if created:
            print(f"  ✓ Added: {product.product_id} - {product.name}")
        else:
            print(f"  - Already exists: {product.product_id}")
    
    # Add denominations
    denominations = [500, 50, 20, 10, 5, 2, 1]
    
    print("\nAdding shop denominations...")
    for value in denominations:
        denom, created = ShopDenomination.objects.get_or_create(
            value=value,
            defaults={'count': 100}
        )
        if created:
            print(f"  ✓ Added: ₹{value} x 100")
        else:
            print(f"  - Already exists: ₹{value} (count: {denom.count})")
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the server: python manage.py runserver")
    print("3. Access the app: http://127.0.0.1:8000/")
    print("4. Access admin: http://127.0.0.1:8000/admin/")
    print("\nSample Product IDs: P001, P002, P003, P004, P005")

if __name__ == '__main__':
    setup()
