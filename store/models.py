from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Choices
CATEGORY_CHOICES = [
    ('abaya', 'Abaya'),
    ('scarf', 'Scarf'),
]

SIZE_CHOICES = [
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
]

COLOR_CHOICES = [
    ('black', 'Black'),
    ('gray', 'Gray'),
    ('navy', 'Navy'),
    ('white', 'White'),
    ('beige', 'Beige'),
]

ORDER_STATUS = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
]

# Product Table
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='black')  # ✅ new
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, default='M')         # ✅ new
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Order Table
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)                     
    color = models.CharField(max_length=50, choices=COLOR_CHOICES)                   
    address = models.TextField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    card_name = models.CharField(max_length=100, blank=True, null=True)
    masked_card = models.CharField(max_length=20, blank=True, null=True)
    expiry = models.CharField(max_length=7, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

# Product Admin Configuration
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'color', 'size', 'created_at')
    fields = ('name', 'description', 'price', 'category', 'color', 'size', 'image')
    search_fields = ('name', 'category')

# Order Admin Configuration
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'product', 'quantity', 'size', 'color', 'status', 'created_at')
    list_filter = ('size', 'color', 'status', 'created_at')
    search_fields = ('customer_name', 'email', 'product__name', 'color')

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'}"


PAYMENT_METHODS = [
    ('paypal', 'PayPal'),
    ('visa', 'Visa'),
    ('cod', 'Cash on Delivery'),
]

payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
is_paid = models.BooleanField(default=False)
