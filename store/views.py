from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q

# Create your views here.

def home(request):
    return render(request, 'home.html')


#-------------------------------------------------
#STEP 4.1: Home Page View (Database → Website)
#-------------------------------------------------
from .models import Product, Category, HomeBanner, Review, ProductImage, ProductVariant

def home(request):
    banners = HomeBanner.objects.filter(is_active=True).order_by('-created_at')
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # Category filter
    category_slug = request.GET.get('category')  # URL Parameter to filter by

    if category_slug:
        products = products.filter(category__slug = category_slug)

    # Search filter
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)

    context = {
        'products': products,
        'categories': categories,
        'banners': banners
    }

    return render(request, 'home.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    variants = product.variants.filter(is_active=True)
    # ✅ Unique sizes
    unique_sizes = sorted(set(
        variants.values_list('size', flat=True)
    ))
    unique_colors = variants.values_list('color', flat=True).distinct()

    images = product.images.all()  # ✅ Get all images for the product

    reviews = product.reviews.all()
    rating_summary = reviews.values('rating').annotate(
        count=Count('rating')
    )
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    return render(request, 'product_detail.html', {'product': product, 'variants': variants, 'unique_sizes':unique_sizes, 'unique_colors': unique_colors, 'images': images, 'reviews': reviews.order_by('-rating'), 'avg_rating': round(avg_rating), 'total_reviews': reviews.count(), 'rating_summary': rating_summary})


#-------------------------------------------------
# STEP 2: Cart Views (Session-Based) -- 2.1 Add to Cart

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    size  = request.POST.get('size')
    color = request.POST.get('color')
    quantity = int(request.POST.get('quantity', 1))

    variant = None
    sku = None

    # 1️⃣ SIMPLE PRODUCT (No Variant)

    if product.product_type == 'simple':
        variant_price = float(product.price)
        cart_key = f"{slug}"

    # 2️⃣ SINGLE VARIANT (Auto Pick First Variant)
    elif product.product_type == 'single':
        variant = product.variants.filter(is_active=True).first()

        if not variant:
            return redirect('product_detail', slug=slug)
        
        variant_price = float(variant.price)
        sku = variant.sku
        cart_key = f"{slug}_{variant.id}"

    # 3️⃣ MULTI VARIABLE PRODUCT (Size + Color Selection)

    elif product.product_type == 'variant':

        if not size or not color:
            return redirect('product_detail', slug=slug)
        
        variant = ProductVariant.objects.filter(
            product=product,
            size=size,
            color=color,
            is_active=True
        ).first()

        if not variant:
            return redirect('product_detail', slug=slug)
        
        variant_price = float(variant.price)
        sku = variant.sku
        cart_key = f"{slug}_{size}_{color}"

    else:
        return redirect('product_detail', slug=slug)
    
    # 🔑 Cart Dictionary in Session

    cart = request.session.get('cart', {})

    # ✅ Save selected product in session for checkout
    #print("✅ ADD TO CART:", size, color, price, quantity)

    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
        cart[cart_key]['subtotal'] = (cart[cart_key]['price'] * cart[cart_key]['quantity'])
    else:
        cart[cart_key] = {
            'product_id': product.id,
            'variant_id': variant.id if variant else None,
            'name': product.name,
            'image': product.image.url,
            'size': size,
            'color': color,
            'sku': sku,
            'price': variant_price,
            'quantity': quantity,
            'subtotal': variant_price * quantity,
            'free_shipping': product.free_shipping,
            'product_slug': product.slug
        }
        
    request.session['cart'] = cart
    request.session['checkout_mode'] = 'cart'
    request.session.modified = True
    
    #print("CART:", request.session['cart'])  # 🔴 DEBUG (TEMPORARY)
    
    return redirect('cart')
#-------------------------------------------------

#-------------------------------------------------
# 2.2 Cart Page View (Total + Items)

def cart_view(request):
    cart = request.session.get('cart', {})

    total_price = sum(
        item['price'] * item['quantity'] for item in cart.values()
        )

    total_items = sum(
        item['quantity'] for item in cart.values()
    )
    return render(request, 'cart.html', {
        'cart': cart,
        'total_price': total_price,
        'total_items': total_items,
    })
#-------------------------------------------------


#-------------------------------------------------
# 2.3 Update Cart Item Quantity(Quantity Increase / Decrease)

def update_cart(request, cart_key):
    cart = request.session.get('cart', {})
    action = request.GET.get('action')

    if cart_key in cart:
        if action == 'increase':
            cart[cart_key]['quantity'] += 1
        elif action == 'decrease':
            if cart[cart_key]['quantity'] > 1:
                cart[cart_key]['quantity'] -= 1

        cart[cart_key]['subtotal'] = (
            cart[cart_key]['price'] * cart[cart_key]['quantity']
        )

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')

#-------------------------------------------------


#-------------------------------------------------
# 2.4 Remove Item from Cart

def remove_from_cart(request, cart_key):
    cart = request.session.get('cart', {})

    if cart_key in cart:
        del cart[cart_key]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')

#-------------------------------------------------


#-------------------------------------------------
# STEP 7.5: Buy Now View (Direct to Checkout)

def buy_now(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    size = request.POST.get('size')
    color = request.POST.get('color')
    quantity = int(request.POST.get('quantity', 1))

    price = request.POST.get('price')
    if product.product_type == "simple":
        final_price = float(product.price)

    else:
        if price and price.strip() != "":
            final_price = float(price)
        else:
            final_price = float(product.price)


    # ✅ Save selected product in session for checkout
    # print("✅ RECEIVED:", size, color, price, quantity)

    request.session['buy_now_item'] = {
        'product_id': product.id,
        'name': product.name,
        'image': product.image.url,
        'size': size,
        'color': color,
        'price': final_price, # Use original price for buy now
        'quantity': quantity,
        'subtotal': final_price * quantity,
        'product_slug': product.slug
    }

    request.session['checkout_mode'] = 'buy_now'
    request.session.modified = True

    return redirect('checkout')
#-------------------------------------------------

#-------------------------------------------------
# STEP 7.4: Checkout View (Cart → Checkout Page)

#-------------------------------------------------

#-------------------------------------------------
# STEP 8: Search Suggestions API (AJAX)

def search_suggest(request):
    q = request.GET.get('q', '')

    suggestions = list(
        Product.objects
        .filter(name__icontains=q, is_active=True)
        .values_list('name', flat=True)[:5]
    )

    return JsonResponse(suggestions, safe=False)

#-------------------------------------------------



#-------------------------------------------------------------------
# STEP 9: Product Reviews View (Submit Review Form)
@login_required
def submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment")

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect('product_detail', slug=slug)
#-------------------------------------------------------------------