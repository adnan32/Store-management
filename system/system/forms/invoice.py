from django import forms
from django.forms import inlineformset_factory
from ..models import Invoice, InvoiceLine

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "customer", "issue_date", "payment_term","due_date",
            "vat_mode", "vat_rate", "notes",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date":   forms.DateInput(attrs={"type": "date"}),
        }

LineFormset = inlineformset_factory(
    Invoice, InvoiceLine,
    fields=["product", "description", "quantity", "unit_price"],
    extra=1, can_delete=True
)
