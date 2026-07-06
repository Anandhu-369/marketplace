from traders.models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cnt=Cart.objects.filter(buyer_object=request.user).count()
        return {"cart_count":cnt}
    else:
        return {"cart_count":0}