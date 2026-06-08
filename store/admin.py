from django.contrib import admin
from .models import Product, Order, Feedback
from django.urls import path
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.admin import AdminSite

# Product admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    

# Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'customer_name', 
        'email', 
        'phone', 
        'address',
        'product', 
        'quantity', 
        'size', 
        'color',
        'payment_method',
        'masked_card',
        'expiry',
        'is_paid',
        'status', 
        'created_at'
    ]
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['customer_name', 'email', 'phone', 'masked_card', 'product__name']
    ordering = ['-created_at']


# Feedback admin
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'created_at']
    search_fields = ['user__username', 'message']
    ordering = ['-created_at']

# PDF report generation
def generate_pdf_report(request):
    orders = Order.objects.all().order_by('-created_at')
    template_path = 'store/pdf_report.html'
    context = {'orders': orders}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating report')
    return response

# Custom admin site
class MyAdminSite(AdminSite):
    site_header = 'Magical Elegance Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sales-report/', self.admin_view(generate_pdf_report), name='sales-report'),
        ]
        return custom_urls + urls

admin_site = MyAdminSite(name='Magical Elegance')
