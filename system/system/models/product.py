from django.db import models

class Product(models.Model):
    name            = models.CharField(max_length=255)
    model           = models.CharField(max_length=255, blank=True)
    category        = models.CharField(max_length=100, blank=True)
    available_qty   = models.PositiveIntegerField(default=0)
    purchase_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier        = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.model})"