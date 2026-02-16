from django.contrib import admin
from .models import Product, Bill, BillItem, ShopDenomination, BalanceDenomination, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'available_stocks', 'price', 'tax_percentage']
    list_filter = ['tax_percentage']
    search_fields = ['product_id', 'name']
    ordering = ['name']


@admin.register(ShopDenomination)
class ShopDenominationAdmin(admin.ModelAdmin):
    list_display = ['value', 'count', 'total_value']
    ordering = ['-value']

    def total_value(self, obj):
        return obj.value * obj.count
    total_value.short_description = 'Total Value'


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'tax_percentage', 'tax_amount', 'total_price']
    can_delete = False


class BalanceDenominationInline(admin.TabularInline):
    model = BalanceDenomination
    extra = 0
    readonly_fields = ['value', 'count']
    can_delete = False


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_email', 'rounded_net_price', 'amount_paid', 'balance', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer_email']
    readonly_fields = [
        'customer_email', 'total_price_without_tax', 'total_tax', 
        'net_price', 'rounded_net_price', 'amount_paid', 'balance', 'created_at'
    ]
    inlines = [BillItemInline, BalanceDenominationInline]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
