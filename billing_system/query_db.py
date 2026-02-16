#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

print('=' * 100)
print('PRODUCTS')
print('=' * 100)
c.execute('SELECT product_id, name, price, available_stocks, tax_percentage FROM billing_product')
for row in c.fetchall():
    print(f"{row[0]:<8} | {row[1]:<30} | Price: {row[2]:<10} | Stock: {row[3]:<5} | Tax: {row[4]}%")

print('\n' + '=' * 100)
print('BILLS')
print('=' * 100)
c.execute('SELECT id, customer_email, rounded_net_price, amount_paid, balance, created_at FROM billing_bill')
for row in c.fetchall():
    print(f"Bill #{row[0]:<3} | {row[1]:<30} | Total: ₹{row[2]:<10} | Paid: ₹{row[3]:<10} | Balance: ₹{row[4]:<10} | {row[5]}")

print('\n' + '=' * 100)
print('USERS')
print('=' * 100)
c.execute('SELECT u.id, u.username, u.email, COALESCE(p.phone, "-"), COALESCE(p.city, "-"), COALESCE(p.state, "-") FROM auth_user u LEFT JOIN billing_userprofile p ON u.id = p.user_id')
for row in c.fetchall():
    print(f"ID: {row[0]:<3} | {row[1]:<20} | {row[2]:<30} | Phone: {row[3]:<15} | City: {row[4]:<15} | State: {row[5]}")

print('\n' + '=' * 100)
print('DENOMINATIONS (SHOP)')
print('=' * 100)
c.execute('SELECT value, count FROM billing_shopdenomination ORDER BY value DESC')
total_value = 0
for row in c.fetchall():
    denom_total = row[0] * row[1]
    total_value += denom_total
    print(f"₹{row[0]:<6} | Count: {row[1]:<4} | Total Value: ₹{denom_total}")
print(f"{'GRAND TOTAL':<8} | {'':4} | Total Value: ₹{total_value}")

print('\n' + '=' * 100)
print('BILL ITEMS')
print('=' * 100)
c.execute('SELECT bi.id, bi.bill_id, bi.product_id, bi.quantity, bi.unit_price, bi.total_price FROM billing_billitem bi')
for row in c.fetchall():
    print(f"Item #{row[0]:<3} | Bill #{row[1]:<3} | Product: {row[2]:<6} | Qty: {row[3]:<3} | Unit: ₹{row[4]:<10} | Total: ₹{row[5]}")

conn.close()
print('\n' + '=' * 100)
