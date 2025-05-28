from django.db import models
from django.utils import timezone
from .customer import Customer
from .product import Product

class Invoice(models.Model):
    VAT_INCLUDED = "inc"
    VAT_EXCLUDED = "exc"
    VAT_CHOICES  = [(VAT_INCLUDED, "VAT included"), (VAT_EXCLUDED, "VAT excluded")]

    number      = models.CharField(max_length=30, unique=True)
    issue_date  = models.DateField(default=timezone.now)
    due_date    = models.DateField()
    customer    = models.ForeignKey(Customer, on_delete=models.SET_NULL,null=True, blank=True,related_name="invoices")
    vat_mode    = models.CharField(max_length=3, choices=VAT_CHOICES, default=VAT_INCLUDED)
    vat_rate    = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    notes       = models.TextField(blank=True)

    def __str__(self):
        return f"INV {self.number}"

    # ── totals ──────────────────────────
    @property
    def total_ex_vat(self):
        return sum(l.total_ex_vat for l in self.lines.all())

    @property
    def vat_total(self):
        return self.total_ex_vat * (self.vat_rate / 100)

    @property
    def total_inc_vat(self):
        return self.total_ex_vat + self.vat_total

class InvoiceLine(models.Model):
    invoice       = models.ForeignKey(Invoice, related_name="lines", on_delete=models.CASCADE)
    product       = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True, blank=True,related_name="invoices")
    description   = models.CharField(max_length=255, blank=True)
    quantity      = models.PositiveIntegerField(default=1)
    unit_price    = models.DecimalField(max_digits=10, decimal_places=2)

    # snapshot copies
    product_name  = models.CharField(max_length=255)
    product_model = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if creating:
            self.product_name  = self.product.name
            self.product_model = self.product.model
        super().save(*args, **kwargs)
        if creating:
            self.product.available_qty -= self.quantity
            self.product.save(update_fields=["available_qty"])

    @property
    def total_ex_vat(self):
        return self.quantity * self.unit_price