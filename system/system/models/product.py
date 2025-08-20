from django.db import models
from django.utils.translation import gettext_lazy as _
class Product(models.Model):
    name            = models.CharField(_("Name"),max_length=255)
    model           = models.CharField(_("Model"),max_length=255, blank=True)
    category        = models.CharField(_("Category"),max_length=100, blank=True)
    available_qty   = models.PositiveIntegerField(_("Available quantity"),default=0)
    purchase_price  = models.DecimalField(_("Purchase Price"),max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price   = models.DecimalField(_("Selling Price"),max_digits=10, decimal_places=2, null=True, blank=True)
    supplier        = models.CharField(_("Supplier"),max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.model})"