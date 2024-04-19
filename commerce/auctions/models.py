from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField(max_length=300, blank=True)
    item_category = models.ManyToManyField(Category)

    def __str__(self):
        return f"{self.title}"

# class Bid(models.Model):
#     pass
