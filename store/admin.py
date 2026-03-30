from django.contrib import admin

#---------------------------------
#STEP 3.1: Models ko Admin Panel me Register karna
#---------------------------------

from .models import Product, Category, ProductAttribute, HomeBanner, ProductImage, ProductVariant, Review


# Register your models here.

#------------------------------------------------
# Product Attribute Inline (already correct)
# ------------------------------------------------
class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
#------------------------------------------------


# ------------------------------------------------
# Product Variant Inline (SIZE + STOCK)
# ------------------------------------------------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
#-------------------------------------------------


# ------------------------------------------------
# Product Image Inline (THUMBNAILS)
# ------------------------------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4
#------------------------------------------------




#---------------------------------
# STEP 3.2: Category ko Admin me Register karo
#---------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


#---------------------------------
# STEP 3.3: Product ko Admin me Register karo
#---------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_type', 'is_best_seller', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'product_type')   # ✅ category FK is valid
    list_editable = ('price', 'is_best_seller', 'is_active')
    search_fields = ('name', 'slug', 'description', 'sku')  # ✅ search by name, slug, description, SKU
    prepopulated_fields = {'slug': ('name',)}  # ✅ slug auto-generate from name


    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'name', 'product_type', 'price', 'mrp', 'image', 'is_active')
        }),
        
        ('Detailed Info', {
            'fields': ('short_description', 'description', 'is_best_seller')
        }),

        ('SEO', {
            'fields': ('slug',)
        }),
    )

    inlines = [
        ProductAttributeInline,   # ✅ attributes
        ProductImageInline,       # ✅ thumbnails
        ProductVariantInline      # ✅ size + stock
        ]  # ✅ inlines for attributes, images, variants
    
#---------------------------------
# STEP 3.4: HomeBanner ko Admin me Register karo
@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_editable = ('is_active',)
#---------------------------------



#------------------------------------------------------------
# Rating ko Admin me Register karna (CONFIRM)
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
#------------------------------------------------------------

#------------------------------------------------------------
# Product Variant Direct Admin (For SKU Search)
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'size', 'color', 'price', 'stock', 'is_active')
    search_fields = ('sku', 'product__name')
    list_filter = ('is_active', 'product')

#--------------------------------------------------------------

