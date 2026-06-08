from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib import messages
from .models import Feedback

# Home page view
def home(request):
    return render(request, 'home.html')

# Product listing page
def product_list(request):
    products = Product.objects.all()

    category = request.GET.get('category')
    color = request.GET.get('color')
    size = request.GET.get('size')

    if category:
        products = products.filter(category=category)
    if color:
        products = products.filter(color=color)
    if size:
        products = products.filter(size=size)

    context = {
        'products': products,
        'selected_category': category,
        'selected_color': color,
        'selected_size': size,
    }
    return render(request, 'product_list.html', context)

# Product detail page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

# Add to cart (POST only)
@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size')
    color = request.POST.get('color')

    cart[str(product_id)] = {
        'quantity': quantity,
        'size': size,
        'color': color,
    }

    request.session['cart'] = cart
    return redirect('cart')

# View & update cart
def view_cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                product_id = key.split('_')[1]
                if value == '0':
                    cart.pop(product_id, None)
                else:
                    if product_id in cart:
                        cart[product_id]['quantity'] = int(value)
        request.session['cart'] = cart
        return redirect('cart')

    cart_items = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        quantity = item['quantity']
        size = item.get('size', '')
        color = item.get('color', '')
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'size': size,
            'color': color,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'cart.html', context)

# Checkout View
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        quantity = item['quantity']
        size = item.get('size')
        color = item.get('color')
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'size': size,
            'color': color,
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order_ids = []
        for item in cart_items:
            order = Order.objects.create(
                customer=request.user,
                customer_name=name,
                email=email,
                address=address,
                phone=phone,
                product=item['product'],
                quantity=item['quantity'],
                size=item['size'],
                color=item['color']
            )
            order_ids.append(order.id)

        request.session['cart'] = {}
        request.session['latest_order_id'] = order_ids[-1]  # store last created order id
        return redirect('payment')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def generate_report_pdf(request):
    orders = Order.objects.all().order_by('-created_at')
    template_path = 'pdf_report.html'
    context = {'orders': orders}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def submit_feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        # Later: Save to DB or email to admin
        print(f"Feedback received: {message}")
        messages.success(request, "Thank you for your feedback!")
        return redirect('home')
    else:
        raise Http404("Page not found")
    

def submit_feedback(request):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=message_text
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('home')
    else:
        raise Http404("Page not found")



# Payment View
@login_required
def payment_view(request):
    order_id = request.session.get('latest_order_id')
    if not order_id:
        return redirect('cart')

    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return redirect('cart')

    if request.method == 'POST':
        method = request.POST.get('payment_method')
        order.payment_method = method
        order.is_paid = True

        # Save additional card info only if method is visa
        if method == 'visa':
            card_name = request.POST.get('card_name')
            card_number = request.POST.get('card_number')
            expiry = request.POST.get('expiry')

            if card_number and len(card_number) >= 4:
                masked = f"**** **** **** {card_number[-4:]}"
                order.masked_card = masked
                order.card_name = card_name
                order.expiry = expiry

        order.save()
        return render(request, 'thank_you.html', {'name': order.customer_name})

    return render(request, 'payment.html')

