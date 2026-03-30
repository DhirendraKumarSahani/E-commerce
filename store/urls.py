from django.urls import path
from .views import home, product_detail, add_to_cart, cart_view, update_cart, remove_from_cart, buy_now, search_suggest, submit_review
urlpatterns = [
    path('', home, name='home'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('add-to-cart/<slug:slug>/', add_to_cart, name='add_to_cart'),  # NEW
    path('cart/', cart_view, name='cart'),  # NEW
    path('update-cart/<str:cart_key>/', update_cart, name='update_cart'),  # NEW
    path('remove-from-cart/<str:cart_key>/', remove_from_cart, name='remove_from_cart'),  # NEW
    path('buy-now/<slug:slug>/', buy_now, name='buy_now'),  # NEW
    path('search-suggest/', search_suggest, name='search_suggest'), # NEW
    path('product/<slug:slug>/review/', submit_review, name='submit_review'), # NEW
]