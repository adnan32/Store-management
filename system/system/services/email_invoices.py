# system/services/email_invoice.py
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from ..models import CompanyProfile

def send_invoice(invoice, to_address):
    company = CompanyProfile.objects.first()
    html = render_to_string("invoices/pdf.html",
                            {"invoice": invoice, "company": company})
    pdf_content = HTML(string=html).write_pdf()

    email = EmailMessage(
        subject=f"Invoice {invoice.number}",
        body="Please find attached your invoice.",
        from_email=company.email or "no-reply@example.com",
        to=[to_address],
    )
    email.attach(f"invoice_{invoice.number}.pdf", pdf_content, "application/pdf")
    email.send()
