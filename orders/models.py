from django.db import models
from django.conf import settings
from store.models import Product
from django.utils import timezone
from datetime import timedelta

# Create your models here.


#-------------------------------------------------
#STEP-3: Order Model (Guest + User both)
#-------------------------------------------------

class Order(models.Model):
    STATUS_CHOICES = [
        ('PLACED', 'Placed'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('RETURN_REQUESTED', 'Return Requested'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),

    ]

    PAYMENT_METHODS = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='COD'
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    guest_email = models.EmailField(blank = True, null = True)
    order_id = models.CharField(max_length = 100, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length= 20,
        choices= [
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('FAILED', 'Failed'),
        ],
        default= 'PENDING'
    )

    order_status = models.CharField(
        max_length= 20,
        choices= STATUS_CHOICES,
        default= 'PLACED'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    
    def __str__(self):
        return self.order_id
    

    def save(self, *args, **kwargs):

        is_new = self._state.adding
        old_status = None

        if not is_new:
            old = type(self).objects.get(pk=self.pk)
            old_status = old.order_status

        super().save(*args, **kwargs)

        # 📜 HISTORY CREATE
        if is_new:
            OrderStatusHistory.objects.create(
                order=self,
                status=self.order_status
            )

        elif old_status != self.order_status:
            OrderStatusHistory.objects.create(
                order=self,
                status=self.order_status
            )

#------------------------------------------------------------------



#-------------------------------------------------
# STEP-4: OrderItem Model (Product inside Order)
#-------------------------------------------------
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    # 🔥 Product snapshot fields
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=255)
    product_slug = models.SlugField()
    product_image = models.CharField(max_length=500)

    # 🔥 Variant snapshot
    sku = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)

    # 🔥 Pricing snapshot
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"


#-------------------------------------------------
#STEP 7.1: Address Model (NEW – REQUIRED)

class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    address_line = models.TextField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
#-------------------------------------------------
# OrderReceive model

class OrderReceive(models.Model):
    order = models.OneToOneField(
        'Order',
        on_delete=models.CASCADE,
        related_name='order_receive'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_packed = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrderReceive - {self.order.order_id}"


# ------------------------------------------------------------------------------------------
# 🔹 Order Status History (Timeline Tracking)
class OrderStatusHistory(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_id} - {self.status}"

#--------------------------------------------------------------------


# -------------------------------------------------------------------
# PROFESSIONAL SHIPMENT MODEL (Amazon-level)


class Shipment(models.Model):

    SHIPMENT_STATUS = [
        ('CREATED', 'Created'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Delivery Failed'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='shipment'
    )

    carrier_name = models.CharField(max_length=100)
    tracking_id = models.CharField(max_length=100, unique=True)

    shipment_status = models.CharField(
        max_length=30,
        choices=SHIPMENT_STATUS,
        default='CREATED'
    )

    shipped_at = models.DateTimeField(null=True, blank=True)
    expected_delivery = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    #----------------------------------------------------------------
    #Optional: Auto-update shipment status based on order status changes
    def save(self, *args, **kwargs):

        is_new = self._state.adding

        old_status = None
        if not is_new:
            old_status = type(self).objects.get(pk=self.pk).shipment_status
        else:
            old_status = self.shipment_status


        super().save(*args, **kwargs)

        # 🔄 Only trigger if status changed
        if old_status != self.shipment_status:

            order = self.order

            # 📦 PACKED
            if self.shipment_status == 'PACKED':
                order.order_status = 'CONFIRMED'
                order.save()

            # 🚚 SHIPPED
            elif self.shipment_status == 'SHIPPED':

                if not self.shipped_at:
                    Shipment.objects.filter(pk=self.pk).update(
                        shipped_at=timezone.now()
                    )


                # Auto expected delivery (3 days later)
                if not self.expected_delivery:
                    self.expected_delivery = timezone.now() + timedelta(days=3)
                    super().save(update_fields=['expected_delivery'])

                order.order_status = 'SHIPPED'
                order.save()

            # 🚛 IN TRANSIT
            elif self.shipment_status == 'IN_TRANSIT':
                pass

            # 🚚 OUT FOR DELIVERY
            elif self.shipment_status == 'OUT_FOR_DELIVERY':
                pass

            # 📦 DELIVERED
            elif self.shipment_status == 'DELIVERED':

                if not self.delivered_at:
                    Shipment.objects.filter(pk=self.pk).update(
                        delivered_at=timezone.now()
                    )

                order.order_status = 'DELIVERED'

                ## ✅ Only mark PAID for COD
                if order.payment_method == 'COD' and order.payment_status == 'PENDING':
                    order.payment_status = 'PAID'
                order.save(update_fields=['order_status', 'payment_status'])
    #-----------------------------------------------------------------------

    def __str__(self):
        return f"Shipment - {self.order.order_id}"
    
#--------------------------------------------------------------------
# ADVANCED SHIPPING RULE ENGINE
class ShippingRule(models.Model):

    SHIPPING_TYPE = [
        ('STANDARD', 'Standard'),
        ('EXPRESS', 'Express'),
    ]

    name = models.CharField(max_length=100)
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPE, default='STANDARD')
    state = models.CharField(max_length=100, blank=True, null=True)
    base_cost = models.DecimalField(max_digits=8, decimal_places=2)
    min_order_free_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.shipping_type})"
#------------------------------------------------------------------