from django.views.generic import (ListView, CreateView,
                                  UpdateView, TemplateView)
from django.db.models import Q
from django.urls import reverse_lazy
from ..models import Customer
from ..forms.customer import CustomerForm


class CustomerDashboardView(ListView):
    """Show last 5 customers."""
    template_name = "customers/dashboard.html"
    queryset      = Customer.objects.all()[:5]   # thanks to ordering Meta


class CustomerListView(ListView):
    """All customers + simple search."""
    template_name = "customers/list.html"
    paginate_by   = 20
    model         = Customer

    def get_queryset(self):
        qs = super().get_queryset()
        q  = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(contact_person__icontains=q) |
                Q(vat_number__icontains=q)
            )
        return qs


class CustomerCreateView(CreateView):
    template_name = "customers/form.html"
    form_class    = CustomerForm
    success_url   = reverse_lazy("customer-list")


class CustomerUpdateView(UpdateView):
    template_name = "customers/form.html"
    form_class    = CustomerForm
    model         = Customer
    success_url   = reverse_lazy("customer-list")
