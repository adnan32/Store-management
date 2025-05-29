from django.db import models

class CompanyProfile(models.Model):
    name       = models.CharField(max_length=255)
    org_number = models.CharField(max_length=50)
    phone      = models.CharField(max_length=30, blank=True)
    email      = models.EmailField(blank=True)
    address    = models.TextField()
    iban       = models.CharField("IBAN",      max_length=34, blank=True, null=True)
    swish      = models.CharField("Swish",     max_length=10, blank=True, null=True)
    bankgiro   = models.CharField("Bankgiro",  max_length=15, blank=True, null=True)
 
    class Meta:
        verbose_name = "Company profile"
        verbose_name_plural = "Company profile"

    def __str__(self):
        return self.name