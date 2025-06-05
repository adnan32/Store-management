from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal   import Decimal

from .customer import Customer
from .product  import Product


class Invoice(models.Model):
    # ── choices & constants ───────────────────────────────────────
    VAT_INCLUDED = "inc"
    VAT_EXCLUDED = "exc"
    VAT_CHOICES  = [(VAT_INCLUDED, "VAT included"),
                    (VAT_EXCLUDED, "VAT excluded")]

    PAYMENT_CHOICES = [(10, "10 days"), (15, "15 days"),
                       (30, "30 days"), (60, "60 days")]

    # ── fields ────────────────────────────────────────────────────
    number        = models.CharField(max_length=30, unique=True)
    issue_date    = models.DateField(default=timezone.now)
    due_date      = models.DateField(blank=True)            # may be filled automatically
    payment_term  = models.PositiveSmallIntegerField(
                        choices=PAYMENT_CHOICES, default=30)

    customer      = models.ForeignKey(
                        Customer, on_delete=models.SET_NULL,
                        null=True, blank=True, related_name="invoices")

    vat_mode      = models.CharField(
                        max_length=3, choices=VAT_CHOICES,
                        default=VAT_INCLUDED)
    vat_rate      = models.DecimalField(max_digits=5, decimal_places=2, default=25)

    notes         = models.TextField(blank=True)
    paid          = models.BooleanField(
                        default=False,
                        help_text="Tick when full payment has been received.")
    VMB           = models.BooleanField(
                        default=False,
                        help_text="VMB?")

    # optional link when this invoice is a “Reminder”
    reminder_of   = models.ForeignKey(
                        "self", null=True, blank=True,
                        related_name="reminders",
                        on_delete=models.SET_NULL)

    # ── housekeeping before save ─────────────────────────────────
    def save(self, *args, **kwargs):
        # 1) auto-set due-date once
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=self.payment_term)

        # 2) force vat_rate to zero when mode is “excluded”
        if self.vat_mode == self.VAT_EXCLUDED:
            self.vat_rate = 0

        super().save(*args, **kwargs)

    # ── calculated totals (read-only properties) ─────────────────
    @property
    def total_ex_vat(self):
        return sum(l.total_ex_vat for l in self.lines.all())

    @property
    def vat_total(self):
        return Decimal("0") if self.vat_rate == 0 \
               else self.total_ex_vat * (self.vat_rate / 100)

    @property
    def total_inc_vat(self):
        return self.total_ex_vat + self.vat_total

    def __str__(self):
        return f"INV {self.number}"


class InvoiceLine(models.Model):
    # ── relations & snapshot fields ───────────────────────────────
    invoice       = models.ForeignKey(
                        Invoice, related_name="lines",
                        on_delete=models.CASCADE)

    product       = models.ForeignKey(
                        Product, on_delete=models.SET_NULL,
                        null=True, blank=True, related_name="invoice_lines")

    description   = models.CharField(max_length=255, blank=True)
    quantity      = models.PositiveIntegerField(default=1)
    unit_price    = models.DecimalField(max_digits=10, decimal_places=2)

    # snapshot of product data at the time of invoicing
    product_name  = models.CharField(max_length=255, blank=True)
    product_model = models.CharField(max_length=255, blank=True)

    # ── line-level save: only snapshot product once ───────────────
    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name  = self.product.name
            self.product_model = getattr(self.product, "model", "")

        super().save(*args, **kwargs)

    # ── line totals ───────────────────────────────────────────────
    @property
    def total_ex_vat(self):
        return self.quantity * self.unit_price
