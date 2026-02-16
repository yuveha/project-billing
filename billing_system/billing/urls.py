from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-bill/', views.generate_bill, name='generate_bill'),
    path('bill/<int:bill_id>/', views.bill_detail, name='bill_detail'),
    path('customer-purchases/', views.customer_purchases, name='customer_purchases'),
    path('products/', views.products_list, name='products_list'),
    path('bills/', views.bills_list, name='bills_list'),
    path('users/', views.users_list, name='users_list'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('user-profile/', views.user_profile_form, name='user_profile_form'),
    path('api/product/<str:product_id>/', views.get_product_info, name='get_product_info'),
]
