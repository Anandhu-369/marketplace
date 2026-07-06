from django.shortcuts import render , redirect
from traders.forms import *
from django.views.generic import *
from django.views import View
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from traders.models import *
# Create your views here.

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
        form_data=Product.objects.all()
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
        form=Profile.objects.get(user=request.user)
        return render(request,"profile.html",{"form_data":form})


class EditProfileView(View):
    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(instance=profile)
        return render(request, "editprofile.html", {"form_data": form})
    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request,"editprofile.html",{"form_data":form})
