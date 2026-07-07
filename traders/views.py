from django.shortcuts import render , redirect
from traders.forms import *
from django.views.generic import *
from django.views import View
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from traders.models import *
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

RAZOR_PAY_KEY="rzp_test_TAcgBnDb4U1Bbl"
RAZOR_PAY_SECRET_KEY="GX6RHOUZDwXGJecxjomSdXXM"
class SignupView(CreateView):
    template_name="signup.html"
    form_class=SignupForm
    success_url=reverse_lazy("signin")

class SigninView(FormView):
    template_name="signin.html"
    form_class=SigninForm
    def post(self, request):
        form_data=SigninForm(data=request.POST)
        if form_data.is_valid():
            uname=form_data.cleaned_data.get('username')
            pswd=form_data.cleaned_data.get('password')
            user=authenticate(request,username=uname,password=pswd)
            if user:
                login(request,user)
                if user.is_superuser==False:
                    return redirect('homepage')
                elif user.is_superuser:
                    return redirect(reverse('admin:index'))
                else:
                    messages.error(request,"Invalid Username or Password")
                    return redirect('signin')
            return render(request,"signin.html",{"form":form_data})

class HomePageView(View):
    def get(self,request):
        form_data=Product.objects.filter(is_purchased=False)
        return render(request,"home.html",{"form_data":form_data})
    
class ProductDetailsView(View):
    def get(self,request,**kwargs):
        pid=kwargs.get('pid')
        form_data=Product.objects.get(id=pid)
        return render(request,"product_details.html",{"form_data":form_data})
    
class ProductCreateView(View):
    def get(self, request):
        form = ProductForm()
        return render(request,"addproduct.html",{"form_data": form})
    def post(self, request):
        form = ProductForm(data=request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            images = request.FILES.getlist("images")
            for img in images:
                ProductImage.objects.create(product=product,image=img)
            return redirect("homepage")
        return render(request, "addproduct.html",{"form_data": form})

class ChatView(View):
    def get(self,request):
        return render(request,"chatpage.html")



class AddToCartView(View):
    def get(self,request,**kwargs):
        cid=kwargs.get('cid')
        product=Product.objects.get(id=cid)
        buyer=request.user
        (object,created)=Cart.objects.get_or_create(product_object=product,buyer_object=buyer)
        if created:
            return redirect('homepage')
        else:
            messages.warning(request,"Course Already Added To Cart !!!")
            return redirect('homepage')
    
class CartListView(View):
    def get(self,request):
        cart_list=Cart.objects.filter(buyer_object=request.user)
        cart_count=cart_list.count()
        cart_total=0
        for i in cart_list:
            cart_total+=i.product_object.price
        return render(request,"cartlist.html",{"data":cart_list,"count":cart_count,"cart_total":cart_total})


class RemoveCartView(View):
    def get(self,request,**kwargs):
        cid=kwargs.get('cid')
        Cart.objects.get(id=cid).delete()
        return redirect('cartlist')
    
class ShowProfileView(View):
    def get(self,request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        return render(request,"profile.html",{"form_data":profile})


class EditProfileView(View):
    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(instance=profile)
        return render(request, "editprofile.html", {"form": form})
    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request,"editprofile.html",{"form":form})
    


class PlaceOrderView(View):
    def get(self,request):
        buyer=request.user
        qs=Cart.objects.filter(buyer_object=buyer)
        cart_total=0
        for i in qs:
            cart_total+=i.product_object.price
        order=Order.objects.create(buyer_object=buyer,total=cart_total)
        for i in qs:
            order.product_object.add(i.product_object)
        qs.delete()
        if cart_total>0:
            client=razorpay.Client(auth=(RAZOR_PAY_KEY,RAZOR_PAY_SECRET_KEY))
            data={"amount":int(cart_total),"currency":"INR","receipt":"order_rcptid_11"}
            payment=client.order.create(data=data)
            print("payment")
            order.razr_pay_order_id=payment.get('id')
            order.save()
            context={
                "razr_pay_key":RAZOR_PAY_KEY,
                "amount":int(cart_total),
                "razr_pay_order_id":payment.get('id')
            }
            return render(request,"payment.html",{"data":context})
        elif cart_total==0:
            order.is_paid=True
            order.save()
            return redirect('homepage')
        return redirect('homepage')
    
@method_decorator(csrf_exempt,name="dispatch")  
class PaymentVerify(View):
    def post(self,request):
        print(request.POST)
        client=razorpay.Client(auth=(RAZOR_PAY_KEY,RAZOR_PAY_SECRET_KEY))
        try:
            client.utility.verify_payment_signature(request.POST)
            rzr_pay_order_id=request.POST.get('razorpay_order_id')
            order=Order.objects.get(razr_pay_order_id=rzr_pay_order_id)
            order.is_paid=True
            order.product_object.is_purchased=True
            order.save()
        except Exception as e:
            print(e)
            print("Failed")
        return redirect('homepage')
    

class AuctionListView(ListView):
    model = Product
    template_name = "auction_list.html"
    context_object_name = "auctions"

    def get_queryset(self):
        return Product.objects.filter(
            product_type="Auction"
        ).select_related("seller", "category")
    
class AuctionDetailView(DetailView):
    model = Product
    template_name = "auction_detail.html"
    context_object_name = "auction"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["bids"] = self.object.bids.select_related(
            "bidder"
        ).order_by("-created_at")

        return context
    
class PlaceBidView(LoginRequiredMixin, View):

    def post(self, request, pk):

        product = get_object_or_404(
            Product,
            pk=pk,
            product_type="Auction"
        )

        if product.auction_status != "live":
            return JsonResponse({
                "success": False,
                "message": "Auction is not live."
            })

        amount = request.POST.get("amount")

        if not amount:
            return JsonResponse({
                "success": False,
                "message": "Enter a bid amount."
            })

        amount = Decimal(amount)

        minimum = (
            product.current_bid
            if product.current_bid
            else product.starting_bid
        )

        if amount <= minimum:
            return JsonResponse({
                "success": False,
                "message": f"Bid must be greater than ₹{minimum}"
            })

        bid = Bid.objects.create(
            product=product,
            bidder=request.user,
            amount=amount
        )

        return JsonResponse({

            "success": True,
            "current_bid": str(product.current_bid),
            "bidder": request.user.username,
            "amount": str(bid.amount)

        })
    
class CurrentBidAPIView(View):

    def get(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        return JsonResponse({

            "current_bid": str(
                product.current_bid
                if product.current_bid
                else product.starting_bid
            ),

            "status": product.auction_status

        })
    
class BidHistoryAPIView(View):

    def get(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        bids = product.bids.select_related(
            "bidder"
        ).order_by("-created_at")[:10]

        data = []

        for bid in bids:

            data.append({

                "user": bid.bidder.username,
                "amount": str(bid.amount),
                "time": bid.created_at.strftime("%I:%M %p")

            })

        return JsonResponse(data, safe=False)
    
class AuctionTimerAPIView(View):

    def get(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        now = timezone.now()

        remaining = (
            product.auction_end - now
        ).total_seconds()

        if remaining < 0:
            remaining = 0

        return JsonResponse({

            "seconds": int(remaining),
            "status": product.auction_status

        })
    
class AuctionWinnerAPIView(View):

    def get(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        if product.auction_status != "ended":
            return JsonResponse({
                "winner": None
            })

        winner = product.bids.order_by("-amount").first()

        if winner:

            return JsonResponse({

                "winner": winner.bidder.username,
                "amount": str(winner.amount)

            })

        return JsonResponse({

            "winner": None

        })
    
class MyBidsView(LoginRequiredMixin, ListView):

    model = Bid
    template_name = "my_bids.html"
    context_object_name = "bids"

    def get_queryset(self):
        return Bid.objects.filter(
            bidder=self.request.user
        ).select_related("product")

class MyAuctionsView(LoginRequiredMixin, ListView):

    model = Product
    template_name = "my_auctions.html"
    context_object_name = "auctions"

    def get_queryset(self):

        return Product.objects.filter(

            seller=self.request.user,
            product_type="Auction"

        )