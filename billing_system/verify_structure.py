#!/usr/bin/env python
"""
Verification script to check if the project structure is correct
"""
import os
import sys

def check_file(filepath, description):
    if os.path.exists(filepath):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING")
        return False

def main():
    print("="*60)
    print("Billing System - Project Structure Verification")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_good = True
    
    # Core files
    print("\nCore Files:")
    all_good &= check_file(os.path.join(base_dir, 'manage.py'), 'manage.py')
    all_good &= check_file(os.path.join(base_dir, 'requirements.txt'), 'requirements.txt')
    all_good &= check_file(os.path.join(base_dir, 'README.md'), 'README.md')
    all_good &= check_file(os.path.join(base_dir, 'QUICKSTART.md'), 'QUICKSTART.md')
    all_good &= check_file(os.path.join(base_dir, 'setup_data.py'), 'setup_data.py')
    
    # Django project files
    print("\nDjango Project Files:")
    all_good &= check_file(os.path.join(base_dir, 'billing_system', '__init__.py'), 'billing_system/__init__.py')
    all_good &= check_file(os.path.join(base_dir, 'billing_system', 'settings.py'), 'billing_system/settings.py')
    all_good &= check_file(os.path.join(base_dir, 'billing_system', 'urls.py'), 'billing_system/urls.py')
    all_good &= check_file(os.path.join(base_dir, 'billing_system', 'wsgi.py'), 'billing_system/wsgi.py')
    
    # Billing app files
    print("\nBilling App Files:")
    all_good &= check_file(os.path.join(base_dir, 'billing', '__init__.py'), 'billing/__init__.py')
    all_good &= check_file(os.path.join(base_dir, 'billing', 'models.py'), 'billing/models.py')
    all_good &= check_file(os.path.join(base_dir, 'billing', 'views.py'), 'billing/views.py')
    all_good &= check_file(os.path.join(base_dir, 'billing', 'urls.py'), 'billing/urls.py')
    all_good &= check_file(os.path.join(base_dir, 'billing', 'admin.py'), 'billing/admin.py')
    all_good &= check_file(os.path.join(base_dir, 'billing', 'apps.py'), 'billing/apps.py')
    
    # Template files
    print("\nTemplate Files:")
    all_good &= check_file(os.path.join(base_dir, 'templates', 'base.html'), 'templates/base.html')
    all_good &= check_file(os.path.join(base_dir, 'templates', 'billing', 'index.html'), 'templates/billing/index.html')
    all_good &= check_file(os.path.join(base_dir, 'templates', 'billing', 'bill_detail.html'), 'templates/billing/bill_detail.html')
    all_good &= check_file(os.path.join(base_dir, 'templates', 'billing', 'customer_purchases.html'), 'templates/billing/customer_purchases.html')
    
    print("\n" + "="*60)
    if all_good:
        print("✓ All files present! Project structure is correct.")
        print("\nNext steps:")
        print("1. pip install -r requirements.txt")
        print("2. python manage.py migrate")
        print("3. python setup_data.py")
        print("4. python manage.py createsuperuser")
        print("5. python manage.py runserver")
    else:
        print("✗ Some files are missing. Please check the structure.")
        sys.exit(1)
    print("="*60)

if __name__ == '__main__':
    main()
