from django.views.generic import ListView,DeleteView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from ..models import Product
from ..forms.product import ProductForm
from django.db.models import Q 

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

# ── dynamic filters ───────────────────────────────────────────
    def get_queryset(self):
        qs = super().get_queryset().order_by("name")

        q = self.request.GET.get("q")          # free-text search
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(model__icontains=q) |
                Q(category__icontains=q)
            )

        cat = self.request.GET.get("category") # category drop-down
        if cat:
            qs = qs.filter(category=cat)

        # numeric ranges
        min_qty  = self.request.GET.get("min_qty")
        max_qty  = self.request.GET.get("max_qty")
        min_prc  = self.request.GET.get("min_price")
        max_prc  = self.request.GET.get("max_price")

        if min_qty: qs = qs.filter(available_qty__gte=min_qty)
        if max_qty: qs = qs.filter(available_qty__lte=max_qty)
        if min_prc: qs = qs.filter(selling_price__gte=min_prc)
        if max_prc: qs = qs.filter(selling_price__lte=max_prc)

        return qs

def get_context_data(self, **kw):
    ctx = super().get_context_data(**kw)
    # distinct list for the category <select>
    ctx["categories"] = (
        Product.objects
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    return ctx

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

class ProductDeleteView(DeleteView):
    model = Product
    template_name = "products/confirm_delete.html"
    success_url   = reverse_lazy("product-list")