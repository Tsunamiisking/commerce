from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    user = models.CharField(max_length=200, default="Anonymous User")
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField(max_length=300, blank=True)
    item_category = models.ManyToManyField(Category)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    user = models.CharField(max_length=200, default="Anonymous User")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.CharField(max_length=500,  blank=True )
    def __str__(self):
        return f"{self.user}: {self.listing}:{self.text}"


class Watchlist(models.Model):
    user = models.CharField(max_length=200, default="ADMIN")
    listings = models.ManyToManyField(Listing)

    def __str__(self):
        return f"{self.user}"


class Bid(models.Model):
    user = models.CharField(max_length=200, default="Anonymous User")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount =  models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user}: Bid {self.amount}"