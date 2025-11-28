from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator



# Create your views here.
def store(request,category_slug=None):
    categories = None
    products = None

    if category_slug !=None:
        categories = get_object_or_404(Category, slug=category_slug) 
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)
    paginator = Paginator(products, 2)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
   
    context ={
        'products': paged_product,
       'count': products.count(),
    }
    
    return render(request, 'store/store.html',context)



def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(
        Product, category__slug=category_slug, slug=product_slug
    )
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
    

    context = {
        'product': product,
        'in_cart': in_cart

    }
    





    return render(request, 'store/product_detail.html', context )
