from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product ,Variation
from .models  import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages 
from django.http import HttpResponse

# هذه الدالة مسؤولة عن إرجاع session id الخاص بالمستخدم
def _cart_id(request):
    # نحاول الحصول على session key الحالي
    cart = request.session.session_key
    
    # لو مفيش session key (يعني أول مرة يدخل)
    if not cart:
        cart = request.session.create()   # ننشئ session جديدة
    
    return cart


def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        ex_var_list = []
        ids = []

        for item in cart_items:
            existing_variation = list(item.variations.all())
            ex_var_list.append(existing_variation)
            ids.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = ids[index]
            item = CartItem.objects.get(id=item_id)
            item.quantity += 1
            item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()

    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if product_variation:
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        try:

            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

        except:
            pass  ### لو الحاجة مش موجودة، ما يعملش حاجة

        return redirect('cart')

   
def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart , id=cart_item_id)
    cart_item.delete()
    return redirect('cart')




#3# دالة عرض السلة
def cart(request, total=0,quantity=0,cart_item=None):
    tax=0
    grand_total=0
    cart_items = []
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items= CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax    
    except ObjectDoesNotExist:
      pass

    

    context ={
        'total': total,
        'quantity': quantity,
       'cart_items': cart_items,
       'tax' : tax,
       'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html',context)
