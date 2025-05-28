from django.urls import path
from .views.customer import (
    CustomerDashboardView, CustomerListView,
    CustomerCreateView, CustomerUpdateView,CustomerDeleteView, 
)
from .views.product import ProductListView, ProductCreateView,ProductDeleteView, ProductUpdateView
from .views.product import ProductDashboardView
from django.urls import path
from .views.home import HomeView
from django.contrib.auth import views as auth_views
from .views.invoice import (
    InvoiceListView, InvoiceCreateView, InvoiceDetailView,
    InvoiceUpdateView, InvoiceDeleteView, InvoicePDFView,InvoiceDashboardView,InvoiceTogglePaidView
)
urlpatterns = [
    path("customers/",          CustomerDashboardView.as_view(), name="customer-dashboard"),
    path("customers/all/",      CustomerListView.as_view(),      name="customer-list"),
    path("customers/add/",      CustomerCreateView.as_view(),    name="customer-add"),
    path("customers/<int:pk>/edit/", CustomerUpdateView.as_view(), name="customer-edit"),
    path("",HomeView.as_view(),name="home"),
    path("login/",auth_views.LoginView.as_view(),name="login-alias"),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('products/dashboard/', ProductDashboardView.as_view(), name='product-dashboard'),
    path("invoices/",                 InvoiceListView.as_view(),   name="invoice-list"),
    path("invoices/add/",             InvoiceCreateView.as_view(), name="invoice-add"),
    path("invoices/<int:pk>/",        InvoiceDetailView.as_view(), name="invoice-detail"),
    path("invoices/<int:pk>/edit/",   InvoiceUpdateView.as_view(), name="invoice-edit"),
    path("invoices/<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("invoices/<int:pk>/pdf/",    InvoicePDFView.as_view(),    name="invoice-pdf"),
    path("invoices/dashboard/", InvoiceDashboardView.as_view(), name="invoice-dashboard"),
    path("customers/<int:pk>/delete/",CustomerDeleteView.as_view(),name="customer-delete"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(),name="product-delete"),
    path("invoices/<int:pk>/paid/",InvoiceTogglePaidView.as_view(),name="invoice-toggle-paid"),
]
