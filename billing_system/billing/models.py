from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


class UserProfile(models.Model):
    """User profile model to store customer details"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.user.email}"


class Product(models.Model):
    """Product model with stock and pricing information"""
    product_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    available_stocks = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Tax percentage (e.g., 18.00 for 18%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['product_id']),
        ]

    def __str__(self):
        return f"{self.product_id} - {self.name}"

    def is_available(self, quantity):
        """Check if requested quantity is available in stock"""
        return self.available_stocks >= quantity


class Bill(models.Model):
    """Bill/Invoice model for customer purchases"""
    customer_email = models.EmailField()
    total_price_without_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    net_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    rounded_net_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_email', '-created_at']),
        ]

    def __str__(self):
        return f"Bill #{self.id} - {self.customer_email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class BillItem(models.Model):
    """Individual items in a bill"""
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class ShopDenomination(models.Model):
    """Available denominations in the shop"""
    value = models.IntegerField(unique=True)
    count = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )

    class Meta:
        ordering = ['-value']

    def __str__(self):
        return f"₹{self.value} x {self.count}"


class BalanceDenomination(models.Model):
    """Denominations returned as balance for a bill"""
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='balance_denominations'
    )
    value = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        ordering = ['-value']

    def __str__(self):
        return f"₹{self.value} x {self.count}"
