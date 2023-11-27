from django.urls import path,include
from .import views

urlpatterns = [
    path('',views.index, name='index'),
    path('product/<int:id>',views.details,name='details'),  # <int:id> is given because the id will be different for different products
    path('success/',views.payment_success_view,name='success'),
    path('failed/',views.payment_failed_view,name="failed"),
    path('api/checkout-session/<int:id>/',views.create_checkout_session,name='api_checkout_session'),
]