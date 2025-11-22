from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product 
from .models  import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages 

# هذه الدالة مسؤولة عن إرجاع session id الخاص بالمستخدم
def _cart_id(request):
    # نحاول الحصول على session key الحالي
    cart = request.session.session_key
    
    # لو مفيش session key (يعني أول مرة يدخل)
    if not cart:
        cart = request.session.create()   # ننشئ session جديدة
    
    return cart



# دالة إضافة منتج إلى السلة
def add_cart(request, product_id):

    # الحصول على المنتج الذي يريد المستخدم إضافته
    product = get_object_or_404(Product, id=product_id)

    # أولًا نحاول إيجاد السلة الخاصة بالمستخدم بناءً على session id
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # لو السلة غير موجودة، ننشئ واحدة جديدة
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()   # حفظ السلة (رغم أن create يحفظ تلقائيًا، لكن لا ضرر)

    
    #### ثانيًا نحاول إيجاد العنصر داخل السلة (CartItem)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
       ## # لو موجود بالفعل → نزيد الكمية#
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        ### لو المنتج لسه أول مرة يدخل السلة → ننشئ عنصر جديد
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()

    # بعد الانتهاء نعيد التوجيه إلى صفحة السلة
    return redirect('cart')


def remove_cart(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = Product.objects.get(id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except (Cart.DoesNotExist, CartItem.DoesNotExist, Product.DoesNotExist):
        pass  ### لو الحاجة مش موجودة، ما يعملش حاجة

    return redirect('cart')

   
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')




#3# دالة عرض السلة
def cart(request, total=0,quantity=0,cart_item=None):
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
       'cart_items' : cart_items,
       'tax' : tax,
       'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html',context)
