from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    name            = models.CharField(_("Company name"), max_length=255)
    contact_person  = models.CharField(_("Contact person"),max_length=255, blank=True)
    phone           = models.CharField(_("Phone"),max_length=30, blank=True)
    address         = models.TextField(_("Address"),blank=True)
    vat_number      = models.CharField(_("VAT / Org. Number"),  max_length=50, blank=True)
    created_at      = models.DateTimeField(default=timezone.now, editable=False)
    email           = models.EmailField(_("Email"),blank=True,null=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
