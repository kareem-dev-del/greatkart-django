from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from .models import Cart,CartItem
from carts.views import _cart_id

# Create your views here.
def store(request,category_slug=None):
    categories = None
    products = None

    if category_slug !=None:
        categories = get_object_or_404(Category, slug=category_slug) 
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)
   
    context ={
        'products': products,
       'count': products.count(),
    }
    
    return render(request, 'store/store.html',context)

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(
        Product, category__slug=category_slug, slug=product_slug
    )
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
    return h


    return render(request, 'store/product_detail.html', {'product': product})
