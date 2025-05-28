from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name            = models.CharField("Company name", max_length=255)
    contact_person  = models.CharField(max_length=255, blank=True)
    phone           = models.CharField(max_length=30, blank=True)
    address         = models.TextField(blank=True)
    vat_number      = models.CharField("VAT / Org-nr", max_length=50, blank=True)
    created_at      = models.DateTimeField(default=timezone.now, editable=False)
    email           = models.EmailField(blank=True,null=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
