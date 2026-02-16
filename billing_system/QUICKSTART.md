# Quick Start Guide

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Initialize Database
```bash
python manage.py migrate
```

## 3. Load Sample Data
```bash
python setup_data.py
```

## 4. Create Admin User
```bash
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

## 5. Run Server
```bash
python manage.py runserver
```

## 6. Access the Application

- **Main Billing Page**: http://127.0.0.1:8000/
- **Customer Purchases**: http://127.0.0.1:8000/customer-purchases/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Sample Product IDs for Testing

- **P001**: Laptop Dell Inspiron (₹50,000 + 18% tax)
- **P002**: Wireless Mouse (₹500 + 12% tax)
- **P003**: Mechanical Keyboard (₹1,500 + 12% tax)
- **P004**: USB Cable (₹150 + 12% tax)
- **P005**: Monitor 24 inch (₹12,000 + 18% tax)

## Test Transaction Example

1. Go to http://127.0.0.1:8000/
2. Enter customer email: customer@example.com
3. Add products:
   - Product ID: P002, Quantity: 2
   - Click "Add New"
   - Product ID: P004, Quantity: 5
4. Enter denominations received:
   - 500: 2
   - 50: 1
5. Enter amount paid: 1050
6. Click "Generate Bill"
7. View the generated bill with balance denominations
8. Check console for email output

## Notes

- Emails are printed to console by default
- For production email, configure SMTP in settings.py
- All denominations start with 100 count each
- Stock is automatically deducted when bills are generated
