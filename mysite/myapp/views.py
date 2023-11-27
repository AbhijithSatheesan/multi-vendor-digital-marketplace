from django.shortcuts import render,reverse
from .models import Product,OrderDetail
from django.conf import settings
import stripe,json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse,HttpResponseNotFound
from django.shortcuts import get_object_or_404


# Create your views here.

def index(request):
    products = Product.objects.all()
    return render(request,'myapp/index.html',{"products":products})

def details(request,id):
    product=Product.objects.get(id=id)
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    return render(request,'myapp/detail.html',{'product':product,'stripe_publishable_key':stripe_publishable_key})

@csrf_exempt
# views.py

# ... (existing imports)

def create_checkout_session(request, id):
    request_data = json.loads(request.body)
    product = get_object_or_404(Product, id=id)  # Fix typo here
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email=request_data['email'],
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100)
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success')) +
        '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('failed')),
    )

    order = OrderDetail()
    order.customer_email = request_data['email']
    order.product = product
    order.stripe_payment_intent = checkout_session['payment_intent']
    order.amount = int(product.price * 100)  # Corrected to use the same unit as in line_items
    order.save()

    return JsonResponse({'sessionId': checkout_session.id})


def payment_success_view(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponseNotFound("Session ID is missing.")
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order = get_object_or_404(OrderDetail, stripe_payment_intent=session.payment_intent)
        order.has_paid = True
        order.save()
        return render(request, 'myapp/payment_success.html', {'order': order})
    except stripe.error.InvalidRequestError:
        return HttpResponseNotFound("Invalid Session ID.")


def payment_failed_view(request):
    return render(request,'myapp/failed.html')
