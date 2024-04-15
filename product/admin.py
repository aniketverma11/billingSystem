from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, BillingMaster

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('uuid','name', 'price', 'description')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)  # Assuming you have a 'status' field in your StatusMixin

@admin.register(BillingMaster)
class BillingMasterAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'totalPrice')
    filter_horizontal = ('products',) 