from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)
from django.http import HttpResponse
from ..models import Invoice, CompanyProfile
from ..forms.invoice import InvoiceForm, LineFormset
from django.utils import timezone
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
import subprocess
from django.views.generic import TemplateView

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
    model         = Invoice
    template_name = "invoices/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["company"] = CompanyProfile.objects.first()     # ← ★ add
        return ctx

WKHTMLTOPDF_EXE = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

class InvoicePDFView(DetailView):
    model = Invoice

    def get(self, request, *args, **kwargs):
        inv = self.get_object()
        company = CompanyProfile.objects.first()
        html_string = render_to_string("invoices/pdf.html", {
            "invoice": inv,
            "company": company,
        })

        # Use the full exe path here
        try:
            proc = subprocess.Popen(
                [WKHTMLTOPDF_EXE, "--quiet", "-", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pdf_bytes, err = proc.communicate(html_string.encode("utf-8"))
            if proc.returncode != 0:
                return HttpResponse(
                    f"PDF generation failed:\n{err.decode('utf-8')}",
                    status=500
                )
        except FileNotFoundError:
            return HttpResponse(
                f"Could not find wkhtmltopdf at {WKHTMLTOPDF_EXE}",
                status=501
            )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice_{inv.number}.pdf"'
        )
        return response
    

class InvoiceDashboardView(TemplateView):
    template_name = "invoices/dashboard.html"
    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["recent"] = Invoice.objects.order_by("-id")[:5]
        ctx["count"]  = Invoice.objects.count()
        ctx["overdue"]  = (
            Invoice.objects
            .filter(paid=False, due_date__lt=timezone.now().date())
            .order_by("due_date")
        )
        ctx["overdue_cnt"] = ctx["overdue"].count()
        return ctx

class InvoiceTogglePaidView(View):
    """Flip the paid flag then bounce back to the list."""
    def post(self, request, pk):
        inv = get_object_or_404(Invoice, pk=pk)
        inv.paid = not inv.paid
        inv.save(update_fields=["paid"])
        return redirect("invoice-list")