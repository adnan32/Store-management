from django import forms
from ..models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'model', 'category',
            'available_qty', 'purchase_price', 'selling_price', 'supplier'
        ]
