from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)
from django.http import HttpResponse
#from weasyprint import HTML
from ..models import Invoice, CompanyProfile
from ..forms.invoice import InvoiceForm, LineFormset

class InvoiceListView(ListView):
    model = Invoice
    template_name = "invoices/list.html"

class InvoiceCreateView(CreateView):
    template_name = "invoices/form.html"
    form_class    = InvoiceForm
    success_url   = reverse_lazy("invoice-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = LineFormset(self.request.POST or None)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        fs  = ctx["formset"]
        if fs.is_valid():
            self.object = form.save(commit=False)
            self.object.number = self._next_number()
            self.object.save()
            fs.instance = self.object
            fs.save()
            return redirect("invoice-detail", pk=self.object.pk)
        return self.render_to_response(ctx)

    def _next_number(self):
        last = Invoice.objects.order_by("-id").first()
        return f"{(last.id if last else 0)+1:06d}"

class InvoiceUpdateView(UpdateView):
    model = Invoice
    template_name = "invoices/form.html"
    form_class    = InvoiceForm
    success_url   = reverse_lazy("invoice-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = LineFormset(self.request.POST or None, instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        fs  = ctx["formset"]
        if fs.is_valid():
            self.object = form.save()
            fs.save()
            return redirect("invoice-detail", pk=self.object.pk)
        return self.render_to_response(ctx)

class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = "invoices/confirm_delete.html"
    success_url   = reverse_lazy("invoice-list")

class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = "invoices/detail.html"

class InvoicePDFView(DetailView):
    model = Invoice

    def get(self, request, *args, **kwargs):
        try:
            from weasyprint import HTML
        except ImportError:
            return HttpResponse(
                "PDF engine not installed on this server.", status=501
            )
        inv = self.get_object()
        company = CompanyProfile.objects.first()
        html = render(request, "invoices/pdf.html", {"invoice": inv, "company": company}).content
        pdf  = HTML(string=html.decode()).write_pdf()
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f"attachment; filename=invoice_{inv.number}.pdf"
        return resp
    
# system/views/invoice.py  (add)
from django.views.generic import TemplateView

class InvoiceDashboardView(TemplateView):
    template_name = "invoices/dashboard.html"
    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["recent"] = Invoice.objects.order_by("-id")[:5]
        ctx["count"]  = Invoice.objects.count()
        return ctx
