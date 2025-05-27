from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "system"

    def ready(self):
        # Runs after Django has finished loading -> no circular-import risk
        from django.contrib import admin
        admin.site.site_header = _("Invoice System — Admin")
        admin.site.index_title = _("Administration")
        admin.site.site_title  = _("Invoice Admin")
