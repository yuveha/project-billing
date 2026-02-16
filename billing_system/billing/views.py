from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from .models import Product, Bill, BillItem, ShopDenomination, BalanceDenomination, UserProfile
import json
import math


def index(request):
    """Main billing page"""
    products = Product.objects.all()
    denominations = ShopDenomination.objects.all()
    return render(request, 'billing/index.html', {
        'products': products,
        'denominations': denominations
    })


def calculate_balance_denominations(balance_amount, shop_denominations):
    """
    Calculate the denominations to return as balance.
    Uses a greedy algorithm to minimize the number of notes/coins.
    """
    balance = int(balance_amount)
    result = []
    
    # Sort denominations by value (highest first)
    sorted_denoms = sorted(shop_denominations, key=lambda x: x.value, reverse=True)
    
    for denom in sorted_denoms:
        if balance <= 0:
            break
            
        if denom.count > 0 and balance >= denom.value:
            # Calculate how many of this denomination we can use
            max_possible = balance // denom.value
            available = min(max_possible, denom.count)
            
            if available > 0:
                result.append({
                    'value': denom.value,
                    'count': available
                })
                balance -= denom.value * available
    
    if balance > 0:
        # Not enough denominations available
        return None
    
    return result


@require_http_methods(["POST"])
@csrf_exempt
@transaction.atomic
def generate_bill(request):
    """Generate bill and send invoice via email"""
    try:
        data = json.loads(request.body)
        
        customer_email = data.get('customer_email', '').strip()
        bill_items = data.get('bill_items', [])
        denomination_counts = data.get('denomination_counts', {})
        amount_paid = Decimal(str(data.get('amount_paid', 0)))
        
        # Validation
        if not customer_email:
            return JsonResponse({'error': 'Customer email is required'}, status=400)
        
        if not bill_items:
            return JsonResponse({'error': 'At least one product is required'}, status=400)
        
        # Update shop denominations
        shop_denominations = []
        for denom in ShopDenomination.objects.all():
            count_to_add = int(denomination_counts.get(str(denom.value), 0))
            denom.count += count_to_add
            denom.save()
            shop_denominations.append(denom)
        
        # Create bill
        bill = Bill.objects.create(
            customer_email=customer_email,
            amount_paid=amount_paid
        )
        
        total_price_without_tax = Decimal('0')
        total_tax = Decimal('0')
        
        # Process each bill item
        for item_data in bill_items:
            product_id = item_data.get('product_id', '').strip()
            quantity = int(item_data.get('quantity', 0))
            
            if not product_id or quantity <= 0:
                continue
            
            try:
                product = Product.objects.select_for_update().get(product_id=product_id)
            except Product.DoesNotExist:
                transaction.set_rollback(True)
                return JsonResponse({'error': f'Product {product_id} not found'}, status=400)
            
            # Check stock availability
            if not product.is_available(quantity):
                transaction.set_rollback(True)
                return JsonResponse({
                    'error': f'Insufficient stock for {product.name}. Available: {product.available_stocks}'
                }, status=400)
            
            # Calculate prices
            unit_price = product.price
            item_total_without_tax = unit_price * quantity
            tax_amount = (item_total_without_tax * product.tax_percentage) / Decimal('100')
            item_total = item_total_without_tax + tax_amount
            
            # Create bill item
            BillItem.objects.create(
                bill=bill,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                tax_percentage=product.tax_percentage,
                tax_amount=tax_amount,
                total_price=item_total
            )
            
            # Update totals
            total_price_without_tax += item_total_without_tax
            total_tax += tax_amount
            
            # Update stock
            product.available_stocks -= quantity
            product.save()
        
        # Calculate final amounts
        net_price = total_price_without_tax + total_tax
        rounded_net_price = Decimal(str(math.ceil(float(net_price))))
        balance = amount_paid - rounded_net_price
        
        # Update bill
        bill.total_price_without_tax = total_price_without_tax
        bill.total_tax = total_tax
        bill.net_price = net_price
        bill.rounded_net_price = rounded_net_price
        bill.balance = balance
        bill.save()
        
        # Calculate balance denominations
        if balance < 0:
            transaction.set_rollback(True)
            return JsonResponse({'error': 'Insufficient payment amount'}, status=400)
        
        balance_denoms = []
        if balance > 0:
            balance_denoms = calculate_balance_denominations(balance, shop_denominations)
            
            if balance_denoms is None:
                transaction.set_rollback(True)
                return JsonResponse({
                    'error': 'Insufficient denominations available to return balance'
                }, status=400)
            
            # Save balance denominations and update shop denominations
            for denom_data in balance_denoms:
                BalanceDenomination.objects.create(
                    bill=bill,
                    value=denom_data['value'],
                    count=denom_data['count']
                )
                
                # Deduct from shop denominations
                shop_denom = ShopDenomination.objects.get(value=denom_data['value'])
                shop_denom.count -= denom_data['count']
                shop_denom.save()
        
        # Send email asynchronously (in production, use Celery or similar)
        send_invoice_email(bill)
        
        return JsonResponse({
            'success': True,
            'bill_id': bill.id,
            'redirect_url': f'/bill/{bill.id}/'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def send_invoice_email(bill):
    """Send invoice email to customer"""
    subject = f'Invoice #{bill.id} - Thank you for your purchase'
    
    # Build email message
    items_text = '\n'.join([
        f"  {item.product.name} x {item.quantity} @ ₹{item.unit_price} = ₹{item.total_price}"
        for item in bill.items.all()
    ])
    
    balance_text = ''
    if bill.balance > 0:
        balance_denoms = '\n'.join([
            f"  ₹{bd.value} x {bd.count}"
            for bd in bill.balance_denominations.all()
        ])
        balance_text = f"\n\nBalance Denominations:\n{balance_denoms}"
    
    message = f"""
Dear Customer,

Thank you for your purchase!

Invoice #: {bill.id}
Date: {bill.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Items Purchased:
{items_text}

Total (without tax): ₹{bill.total_price_without_tax}
Total Tax: ₹{bill.total_tax}
Net Price: ₹{bill.net_price}
Rounded Price: ₹{bill.rounded_net_price}
Amount Paid: ₹{bill.amount_paid}
Balance: ₹{bill.balance}{balance_text}

Thank you for shopping with us!

Best regards,
Billing System
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [bill.customer_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")


def bill_detail(request, bill_id):
    """Display bill details"""
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'billing/bill_detail.html', {'bill': bill})


def customer_purchases(request):
    """View all purchases by a customer"""
    customer_email = request.GET.get('email', '').strip()
    
    if not customer_email:
        return render(request, 'billing/customer_purchases.html', {
            'bills': [],
            'customer_email': ''
        })
    
    bills = Bill.objects.filter(customer_email=customer_email).prefetch_related('items__product')
    
    return render(request, 'billing/customer_purchases.html', {
        'bills': bills,
        'customer_email': customer_email
    })


def products_list(request):
    """Show list of products (for browser viewing)"""
    products = Product.objects.all()
    return render(request, 'billing/products.html', {'products': products})


def bills_list(request):
    """Show list of bills (for browser viewing)"""
    bills = Bill.objects.all().prefetch_related('items__product')
    return render(request, 'billing/bills.html', {'bills': bills})


def get_product_info(request, product_id):
    """API endpoint to get product information"""
    try:
        product = Product.objects.get(product_id=product_id)
        return JsonResponse({
            'success': True,
            'product': {
                'name': product.name,
                'price': str(product.price),
                'tax_percentage': str(product.tax_percentage),
                'available_stocks': product.available_stocks
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)


def users_list(request):
    """Show list of users (for browser viewing)"""
    users = UserProfile.objects.select_related('user').all()
    return render(request, 'billing/users.html', {'users': users})


def user_detail(request, user_id):
    """Show user profile details"""
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    bills = Bill.objects.filter(customer_email=user_profile.user.email).prefetch_related('items__product')
    return render(request, 'billing/user_detail.html', {
        'user_profile': user_profile,
        'bills': bills
    })


def user_profile_form(request):
    """Form to create or update user profile"""
    from django.contrib.auth.models import User
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        
        if not username or not email:
            return render(request, 'billing/user_profile_form.html', {
                'error': 'Username and email are required'
            })
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        
        # Update user if it already existed
        if not created:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        
        # Get or create user profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Update profile
        profile.phone = phone
        profile.address = address
        profile.city = city
        profile.state = state
        profile.postal_code = postal_code
        profile.save()
        
        return render(request, 'billing/user_profile_form.html', {
            'success': f'User profile saved successfully! Username: {username}',
            'user_id': user.id
        })
    
    return render(request, 'billing/user_profile_form.html')
