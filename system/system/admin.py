from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Customer, Product
from .models import Invoice, InvoiceLine, CompanyProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ("name", "contact_person", "vat_number", "phone", "created_at")
    search_fields = ("name", "contact_person", "vat_number")
    list_filter   = ("created_at",)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "category", "available_qty", "selling_price")
    search_fields = ("name", "model", "category", "supplier")

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "issue_date", "total_inc_vat", "paid")
    inlines = [InvoiceLineInline]
    list_filter  = ("paid",)
admin.site.register(CompanyProfile)