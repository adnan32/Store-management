from django import forms
from ..models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model  = Customer
        fields = ["name", "contact_person", "phone",
                  "address", "vat_number"]
