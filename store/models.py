from django.db import models
from category.models import Category
from django.urls import reverse
from django.core.exceptions import ValidationError

# Create your models here.
class Product(models.Model):
    product_name    =models.CharField(max_length=200, unique=True)
    slug            =models.SlugField(max_length=200, unique=True)
    description     =models.TextField(blank=True)
    price           =models.IntegerField()
    images          =models.ImageField(upload_to='phtos/products')
    stock           =models.IntegerField()
    is_available    =models.BooleanField(default=True)
    category        =models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    =models.DateTimeField(auto_now_add=True)
    modified_date   =models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug, self.slug])
    def __str__(self):
        return self.product_name
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    
    
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)
    
    

variation_category_choice =(
    ('color', 'color'),
    ('size', 'size'),

)

class Variation(models.Model):
    product            = models.ForeignKey(Product, on_delete=models.CASCADE)   
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value    = models.CharField(max_length=100)
    is_active          =models.BooleanField(default=True)
    created_date       =models.DateTimeField(auto_now=True)


    objects = VariationManager()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'variation_value'], name='unique_variation_per_product')
        ]

    def clean(self):
        # تحقق إذا كان هناك نفس القيمة لنفس المنتج
        if Variation.objects.filter(product=self.product, variation_value=self.variation_value).exclude(pk=self.pk).exists():
            raise ValidationError("هذه القيمة موجودة بالفعل لهذا المنتج.")

    def save(self, *args, **kwargs):
        self.full_clean() # ينفذ التحقق قبل الحفظ
        super().save(*args, **kwargs)    



    def __str__(self):
     return f"{self.product.product_name} - {self.variation_value}"

   