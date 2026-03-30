from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Create your models here.


#-------------------------------------------------
# STEP-1: Category Model (Sabse basic)
#-------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
#-------------------------------------------------
    



#====================================================================
# STEP-2: Product Model (MOST IMPORTANT)
#-------------------------------------------------
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete = models.CASCADE,
        related_name = 'products'

    )

    PRODUCT_TYPE_CHOICES = (
        ("simple", "Simple (No Variant)"),
        ("single", "Single Variant"),
        ("variant", "Multi Variant"),
    )

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default="simple"
    )


    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    free_shipping = models.BooleanField(default=False)
    short_description = models.CharField(max_length=300, blank=True)
    is_best_seller = models.BooleanField(default=False)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    is_active = models.BooleanField(default=True)

    ## 🔥 NEW DETAIL FIELDS 


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#-------------------------------------------------
# STEP-3: Product Model me slug auto-generate karo (CONFIRM)
    slug = models.SlugField(unique=True ,blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
#-------------------------------------------------
    
    def __str__(self):
        return self.name
#====================================================================


#-------------------------------------------------
# ProductImage (4 Thumbnails)
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/thumbnails/')

    def __str__(self):
        return f"Image of {self.product.name}"
#-------------------------------------------------


#-------------------------------------------------
# STEP-4: ProductVariant (SIZE + STOCK)
class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(max_length=100, unique=True)

    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'size', 'color')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

#-----------------------------------------------------



#-------------------------------------------------
# Dynamic Product Detail Fields 
class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value}"
#-------------------------------------------------



#-------------------------------------------------
# Banner model (Optional)
class HomeBanner(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
#-------------------------------------------------

#-------------------------------------------------
# Customer Review Model (Optional)  
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField()  # 1–5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating', '-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐"
#-------------------------------------------------

