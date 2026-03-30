from django.urls import path
from .views import checkout, place_order, order_success, my_orders, request_return, order_tracking, cancel_order

#-------------------------------------------------
# STEP 1: Checkout URL Pattern
urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('order-success/<str:order_id>/', order_success, name='order_success'),
    path('my-orders/', my_orders, name='my_orders'),  # STEP 9.3: My Orders Page
    path('return/<str:order_id>/', request_return, name='request_return'),  # STEP 10.3: Request Return
    path('cancel/<str:order_id>/', cancel_order, name ='cancel_order'),
    path('track/<str:order_id>/', order_tracking, name='order_tracking'),  # STEP 9.4: Order Tracking
]
#-------------------------------------------------
