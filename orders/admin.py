from django.contrib import admin
from .models import Order, OrderItem, Address, OrderReceive, OrderStatusHistory, Shipment, ShippingRule
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone


# -----------------------------
# ORDER ITEM INLINE (Snapshot View)
# -----------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product_name',
        'product_slug',
        'sku',
        'size',
        'color',
        'price',
        'quantity',
        'total',
        'created_at',
    )
    can_delete = False
    show_change_link = False


#----------------------------------------------------------------


#----------------------------------------------------------------


#---------------------------------------------------------------
# Order Status History Admin (Optional)
class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'created_at')
#---------------------------------------------------------------


#---------------------------------------------------------------
# Shipment History Admin (Optional)
class ShipmentInline(admin.StackedInline):
    model = Shipment
    extra = 0
#---------------------------------------------------------------


# ===============================
# 🔹 Order ADMIN
# ===============================

# -----------------------------
# ORDER ADMIN
# -----------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'user',
        'total_price',
        'payment_status',
        'order_status',
        'created_at',
        'formatted_created_at',
    )

    list_filter = (
        'payment_status',
        'order_status',
        'created_at',
    )

    search_fields = (
        'order_id',
        'guest_email',
        'user__username',
    )

    readonly_fields = (
        'order_id',
        'total_price',
        'created_at',
        'updated_at',
        'address_block',
    )




    inlines = [OrderItemInline, OrderStatusHistoryInline, ShipmentInline]  # ✅ Show order items and status history in order detail

    ordering = ('-created_at',)

    # Address block for order detail view
    def address_block(self, obj):
        if obj.address:
            return(
                f"Name : {obj.address.full_name}\n \n"
                f"Phone : {obj.address.phone}\n \n"
                f"Email : {obj.address.email}\n \n"
                f"Full Address : {obj.address.address_line}\n \n"
                f"City : {obj.address.city} \n \n State : {obj.address.state} \n \n PINCODE : {obj.address.pincode} \n \n"
            )
        return "No address"
    address_block.short_description = "Delivery Address"

    # ✅ Safe formatted datetime
    def formatted_created_at(self, obj):
        local_time = timezone.localtime(obj.created_at)
        return local_time.strftime("%d %b %Y, %I:%M %p")
    
    formatted_created_at.short_description = "Order Date"

# -----------------------------
# ORDER ITEM ADMIN (Standalone)
# -----------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product_name',
        'sku',
        'size',
        'color',
        'quantity',
        'price',
        'total',
        'created_at',
    )

    list_filter = ('created_at',)

    search_fields = (
        'product_name',
        'sku',
        'order__order_id',
    )

    readonly_fields = (
        'product_name',
        'product_slug',
        'sku',
        'size',
        'color',
        'price',
        'quantity',
        'total',
        'created_at',
    )

    ordering = ('-created_at',)
#---------------------------------------------------------------


# -----------------------------
# ADDRESS ADMIN
# -----------------------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'phone',
        'city',
        'state',
        'pincode',
        'created_at',
    )

    search_fields = (
        'full_name',
        'phone',
        'city',
        'pincode',
    )

    ordering = ('-created_at',)
#---------------------------------------------------------------

# -----------------------------
# ORDER RECEIVE ADMIN
# -----------------------------
@admin.register(OrderReceive)
class OrderReceiveAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'is_packed',
        'is_shipped',
        'is_delivered',
        'created_at',
    )

    list_filter = (
        'is_packed',
        'is_shipped',
        'is_delivered',
    )

    readonly_fields = ('created_at',)

    # 🔗 ORDER clickable
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_id)

    order_link.short_description = 'ORDER'

    # 🔗 USER clickable
    def user_link(self, obj):
        if obj.user:
            url = reverse(
                f'admin:{obj.user._meta.app_label}_{obj.user._meta.model_name}_change',
                args=[obj.user.id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return '-'

    user_link.short_description = 'USER'

    # 🔗 ADDRESS clickable
    def address_link(self, obj):
        if obj.address:
            url = reverse('admin:orders_address_change', args=[obj.address.id])
            return format_html('<a href="{}">{}</a>', url, obj.address.full_name)
        return '-'

    address_link.short_description = 'ADDRESS'

#--------------------------------------------------------------------
# Admin Registration
@admin.register(ShippingRule)
class ShippingRuleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'shipping_type',
        'state',
        'base_cost',
        'min_order_free_shipping',
        'shipping_cost',
        'is_active'
    )
     
    list_filter = (
        'shipping_type',
        'is_active',
        'state',
    )

    search_fields = (
        'name',
        'state',
    )

    list_editable = (
        'is_active',
        'base_cost',
        'shipping_cost',
    )

    ordering = ('shipping_type', 'state')

#--------------------------------------------------------------------


