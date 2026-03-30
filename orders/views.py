from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, Address, OrderReceive, Shipment
from .utils import calculate_shipping
from store.models import Product, ProductVariant
from django.contrib.auth.decorators import login_required
import uuid
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
#-------------------------------------------------
# STEP 7.4: Checkout View (Cart → Checkout Page)
def checkout(request):

    # If mode passed via URL
    mode = request.GET.get('mode')
    # print("🔥 CHECKOUT VIEW HIT")
    # print("SESSION:", dict(request.session))

    shipping_type = request.GET.get('shipping_type', 'STANDARD')
    state = "Haryana" # temporary default

    if mode:
        request.session['checkout_mode'] = mode
        request.session.modified = True

    cart = request.session.get('cart', {})
    buy_now = request.session.get('buy_now_item')
    checkout_mode = request.session.get('checkout_mode')

    # 🔹 BUY NOW FLOW

    if checkout_mode == 'buy_now' and buy_now:

        items = [buy_now]

        total_price = sum(
            float(item['price'])*int(item['quantity'])
            for item in items
        )

        shipping_cost = calculate_shipping(
            items,
            state = state,
            shipping_type = shipping_type
        )

        grand_total = total_price + shipping_cost

        return render(request, 'checkout.html', {
            'checkout_item': buy_now,
            'total_price': total_price,
            'shipping_cost': shipping_cost,
            'grand_total': grand_total,
            'order_source': 'buy_now'
        })

    # 🔹 CART FLOW
    if checkout_mode == 'cart' and cart:

        items = list(cart.values())

        total_price = sum(
            item['price'] * item['quantity']
            for item in cart.values()
        )

        state = request.GET.get('state', 'Haryana')
        shipping_type = request.GET.get('shipping_type', 'STANDARD')

        shipping_cost = calculate_shipping(
            items,
            state,
            shipping_type
        )

        grand_total = total_price + shipping_cost 

        return render(request, 'checkout.html', {
            'cart': cart,
            'total_price': total_price,
            'shipping_cost': shipping_cost,
            'grand_total': grand_total,
            'order_source': 'cart'
        })

    return redirect('home')


#-------------------------------------------------


#-------------------------------------------------
# STEP 8.2.1: Buy Now View (Direct to Checkout)
@transaction.atomic
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart = request.session.get('cart', {})
    buy_now = request.session.get('buy_now_item')
    mode = request.session.get('checkout_mode')

    # 1️⃣ Determine items based on mode
    if mode == 'buy_now' and buy_now:
        items = [buy_now]

    elif mode == 'cart' and cart:
        items = list(cart.values())

    else:
        return redirect('home')

    # 2️⃣ Validate Address
    full_name = request.POST.get('full_name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    address_line = request.POST.get('address_line')
    city = request.POST.get('city')
    state = request.POST.get('state')
    pincode = request.POST.get('pincode')

    if not all([full_name, phone, email, address_line, city, state, pincode]):
        return redirect('checkout')
    
    # 3️⃣ Calculate total price
    total_price = sum(
        float(item['price']) * int(item['quantity']) for item in items
    )

    # 4️⃣ Create Address
    address = Address.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        phone=phone,
        email=email,
        address_line=address_line,
        city=city,
        state=state,
        pincode=pincode
    )

    payment_method = request.POST.get('payment_method')

     # 5️⃣ Create Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        guest_email=email,
        order_id=str(uuid.uuid4()).split('-')[0].upper(),
        total_price=total_price,
        payment_status='PENDING',
        payment_method = payment_method,
        order_status='PLACED',
        address=address 
    )

     # 6️⃣ Create Order Items

    for item in items:

        quantity = int(item.get('quantity'))

        variant = ProductVariant.objects.select_for_update().filter(
            product_id=item.get('product_id'),
            size=item.get('size'),
            color=item.get('color'),
            is_active=True
        ).first()

        # 🔥 Stock check
        if variant:
            if variant.stock < quantity:
                messages.error(request, f"{variant.product.name} ({variant.size}, {variant.color}) is out of stock.")
                return redirect('cart')
            
            # STOCK DEDUCTION
            variant.stock -= quantity
            variant.save()

            sku_value = variant.sku
        
        else:
            sku_value = None

        # # 🔥 Variant fetch karo size + color se
        # variant = ProductVariant.objects.filter(
        #     product_id=item.get('product_id'),
        #     size=item.get('size'),
        #     color=item.get('color'),
        #     is_active=True
        # ).first()

        # sku_value = variant.sku if variant else None

        OrderItem.objects.create(
            order=order,
            product_id=item.get('product_id'),
            product_name=item.get('name'),
            product_slug=item.get('product_slug'),
            product_image=item.get('image'),
            sku= sku_value,
            size=item.get('size'),
            color=item.get('color'),
            price=Decimal(item.get('price')),
            quantity= quantity,
            total=Decimal(item.get('price')) * quantity,
        )

    #print("ITEM DATA:", item)

    # 7️⃣ ORDER RECEIVE CREATE

    OrderReceive.objects.create(
        order = order,
        user = request.user if request.user.is_authenticated else None,
        address = address
    )
    
    # 8️⃣ Clear session safely

    if mode == 'cart':
        request.session.pop('cart', None)

    elif mode == 'buy_now':
        request.session.pop('buy_now_item', None)

    request.session.pop('checkout_mode', None)
    request.session.modified = True

    # 9️⃣ Handle Payment Method (COD)

    if request.POST.get('payment_method') == 'COD':
        order.payment_status = 'PENDING'
        order.order_status = 'PLACED'
        order.save()
        return redirect('order_success', order_id=order.order_id)

    return redirect('order_success', order_id=order.order_id)

#-------------------------------------------------

#-------------------------------------------------
# STEP 8.3: Order Success Page

def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'order_success.html', {
        'order': order
    })
#-------------------------------------------------


#-------------------------------------------------
# ✅ STEP-2: User – My Orders + Tracking

@login_required
def my_orders(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .select_related('address', 'shipment')
        .prefetch_related('items', 'status_history')
        .order_by('-created_at')
    )

    return render(request, 'orders/my_orders.html', {
        'orders': orders
    })

#-------------------------------------------------



#-------------------------------------------------
# ✅ STEP-3: User – Request Return

@login_required
def request_return(request, order_id):
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    if order.order_status == 'DELIVERED':
        order.order_status = 'RETURN_REQUESTED'
        order.save()

    return redirect('my_orders')


#--------------------------------------------------------------
# ORDER TRACKING VIEW (Optional)

def order_tracking(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    history = order.status_history.all()

    return render(request, 'orders/order_tracking.html', {
        'order': order,
        'history': history
    })

#---------------------------------------------------------------
# CANCEL ORDER VIEW
@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    if order.order_status in ['PLACED', 'CONFIRMED']:
        order.order_status = 'CANCELLED'
        order.save()

    return redirect('my_orders')
#----------------------------------------------------------------------
@login_required
def payment_success(request, order_id):

    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    if order.payment_method == 'ONLINE':
        order.payment_status = 'PAID'
        order.order_status = 'CONFIRMED'
        order.save()

    return redirect('order_success', order_id=order.order_id)
