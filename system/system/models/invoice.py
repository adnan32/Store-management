from django.db import models
from django.utils import timezone
from .customer import Customer
from .product import Product
from datetime import timedelta
from decimal import Decimal

class Invoice(models.Model):
    VAT_INCLUDED = "inc"
    VAT_EXCLUDED = "exc"
    VAT_CHOICES  = [(VAT_INCLUDED, "VAT included"), (VAT_EXCLUDED, "VAT excluded")]
    PAYMENT_CHOICES = [(10, "10 days"),(15, "15 days"),(30, "30 days"),(60, "60 days"),]

    number      = models.CharField(max_length=30, unique=True)
    issue_date  = models.DateField(default=timezone.now)
    due_date    = models.DateField()
    payment_term   = models.PositiveSmallIntegerField(choices=PAYMENT_CHOICES,default=30)
    customer    = models.ForeignKey(Customer, on_delete=models.SET_NULL,null=True, blank=True,related_name="invoices")
    vat_mode    = models.CharField(max_length=3, choices=VAT_CHOICES, default=VAT_INCLUDED)
    vat_rate    = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    notes       = models.TextField(blank=True)
    paid = models.BooleanField(
        default=False,
        help_text="Tick when full payment has been received."
    )
    def __str__(self):
        return f"INV {self.number}"
    reminder_of = models.ForeignKey(  
        "self", null=True, blank=True,
        related_name="reminders",
        on_delete=models.SET_NULL
    )
    
    # ── automatically zero-out VAT when mode is "exc" ──────────────
    def save(self, *args, **kwargs):
        if self.vat_mode == self.VAT_EXCLUDED:
            self.vat_rate = 0
        super().save(*args, **kwargs)

    # ── totals ─────────────────────────────────────────────────────
    @property
    def total_ex_vat(self):
        return sum(l.total_ex_vat for l in self.lines.all())

    @property
    def vat_total(self):
        if self.vat_rate == 0:
            return 0
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
        # auto-zero VAT if excluded
        if self.vat_mode == self.VAT_EXCLUDED:
            self.vat_rate = 0
        # auto-set due date once
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=self.payment_term)
        super().save(*args, **kwargs)

    @property
    def total_ex_vat(self):
        return self.quantity * self.unit_price