from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)
from django.http import HttpResponse
from django.db.models import Q
from ..models import Invoice, CompanyProfile, Customer
from ..forms.invoice import InvoiceForm, LineFormset
from django.utils import timezone
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
import subprocess
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.conf import settings
WKHTMLTOPDF_EXE = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
class InvoiceListView(ListView):
    model = Invoice
    template_name = "invoices/list.html"
    paginate_by   = 25         
    def get_queryset(self):

        qs = (super()
                .get_queryset()
                .select_related("customer")
                .order_by("-issue_date", "-id"))

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(number__icontains=q) |
                Q(customer__name__icontains=q)
            )

        cust = self.request.GET.get("customer")
        if cust:
            qs = qs.filter(customer__id=cust)

        d_from = self.request.GET.get("from")
        d_to   = self.request.GET.get("to")
        if d_from:
            qs = qs.filter(issue_date__gte=d_from)
        if d_to:
            qs = qs.filter(issue_date__lte=d_to)

        paid = self.request.GET.get("paid")
        if paid == "yes":
            qs = qs.filter(paid=True)
        elif paid == "no":
            qs = qs.filter(paid=False)

        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        # list of customers for the dropdown
        ctx["customers"] = Customer.objects.order_by("name")
        return ctx
class InvoiceSendView(View):
    """
    Generate the invoice PDF and email it to the customer
    using the company’s email settings.
    """

    def post(self, request, pk):
        invoice = Invoice.objects.get(pk=pk)
        company = CompanyProfile.objects.first()

        # 1. Render HTML to string
        html_string = render_to_string(
            "invoices/pdf.html",
            {"invoice": invoice, "company": company}
        )

        # 2. Generate PDF via wkhtmltopdf
        try:
            proc = subprocess.Popen(
                [WKHTMLTOPDF_EXE, "--quiet", "-", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pdf_bytes, error = proc.communicate(html_string.encode("utf-8"))
            if proc.returncode != 0:
                raise RuntimeError(error.decode())
        except Exception as e:
            # Log e in real life
            return HttpResponse(
                f"Could not generate PDF: {e}", status=500
            )

        # 3. Build email
        subject = f"Invoice #{invoice.number} from {company.name}"
        body = (
            f"Dear {invoice.customer.name},\n\n"
            f"Please find attached invoice #{invoice.number}.\n"
            "Let us know if you have any questions.\n\n"
            f"Best regards,\n{company.name}"
        )
        from_email = settings.DEFAULT_FROM_EMAIL  # e.g. "billing@yourcompany.com"
        to_email = [invoice.customer.email]

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to_email,
        )
        email.attach(f"Invoice-{invoice.number}.pdf", pdf_bytes, "application/pdf")

        # 4. Send it!
        try:
            email.send(fail_silently=False)
        except Exception as e:
            return HttpResponse(
                f"Failed to send email: {e}", status=500
            )

        # 5. Redirect back with a success message
        # (You can also use Django’s messages framework)
        return HttpResponseRedirect(
            reverse("invoice-detail", args=[invoice.pk])
        )
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
        return f"{(last.id if last else 0),1:06d}"

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