from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):
    options=[
        ("FixedPrice","FixedPrice"),
        ("Auction","Auction")
    ]
    product_type=models.CharField(max_length=100,choices=options,default="FixedPrice")
    title=models.CharField(max_length=100)
    description=models.CharField(max_length=500)
    price=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
    starting_bid=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="product_category")
    is_negotiatable=models.BooleanField(default=False)
    is_purchased=models.BooleanField(default=False)
    auction_start=models.DateTimeField(null=True,blank=True)
    auction_end=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    current_bid=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
    seller = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="products",
    null=True,
    blank=True
)
    

    class Meta:
        ordering=["-created_at"]
    def __str__(self):
        return self.title

    @property
    def auction_status(self):
        if self.product_type != "Auction":
            return None

        if not self.auction_start or not self.auction_end:
            return "invalid"

        now = timezone.now()

        if now < self.auction_start:
            return "scheduled"

        if now < self.auction_end:
            return "live"

        return "ended"

    def clean(self):
        if self.product_type == "FixedPrice":
            if self.price is None:
                raise ValidationError(
                    {"price": "Fixed-price products require a price."}
                )

        if self.product_type == "Auction":
            if self.starting_bid is None:
                raise ValidationError(
                    {"starting_bid": "Auction products require a starting bid."}
                )

            if not self.auction_start:
                raise ValidationError(
                    {"auction_start": "Auction start is required."}
                )

            if not self.auction_end:
                raise ValidationError(
                    {"auction_end": "Auction end is required."}
                )

            if self.auction_end <= self.auction_start:
                raise ValidationError(
                    {"auction_end": "Auction end must be after auction start."}
                )


class Bid(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    bidder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-amount"]

    def __str__(self):
        return f"{self.bidder} - {self.amount}"

    def clean(self):
        if self.product.product_type != "Auction":
            raise ValidationError(
                "Bids can only be placed on auction products."
            )

        if self.product.auction_status != "live":
            raise ValidationError(
                "Auction is not currently live."
            )

        minimum_bid = (
            self.product.current_bid
            if self.product.current_bid is not None
            else self.product.starting_bid
        )

        if self.amount <= minimum_bid:
            raise ValidationError(
                f"Bid must be greater than {minimum_bid}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if self.product.current_bid is None or self.amount > self.product.current_bid:
            self.product.current_bid = self.amount
            self.product.save(update_fields=["current_bid"])

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=100)
    address=models.TextField(null=True)
    image=models.ImageField(upload_to="Profile_Images",default="user.img")
    latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)
    longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)

    def __str__(self):
        return self.user.username

    @receiver(post_save,sender=User)    
    def create_instructor_profile(sender,instance,created,**kwargs):
        if created and instance:
            Profile.objects.create(user=instance)
    

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name="messages")
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name="messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="products/")

class Order(models.Model):
    product_object=models.ManyToManyField(Product,related_name="product")
    buyer_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name="purchase")
    is_paid=models.BooleanField(default=False)
    razr_pay_order_id=models.CharField(max_length=100,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    total=models.DecimalField(max_digits=10,decimal_places=2)
    

class Cart(models.Model):
    product_object=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="cart_product_items")
    buyer_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name="cart_user_items")
    added_at=models.DateTimeField(auto_now_add=True)
    
