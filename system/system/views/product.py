from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from ..models import Product
from ..forms.product import ProductForm

class ProductDashboardView(TemplateView):
    template_name = "products/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["products"]  = Product.objects.order_by("-id")[:5]
        ctx["low_stock"] = Product.objects.filter(available_qty__lt=5)
        ctx["total"]     = Product.objects.count()
        return ctx

class ProductListView(ListView):
    model = Product
    template_name = "products/list.html"
    paginate_by = 20

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/form.html"
    success_url = reverse_lazy("product-list")

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/form.html"
    success_url = reverse_lazy("product-list")