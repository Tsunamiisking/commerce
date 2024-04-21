from django.contrib import admin
from .models import Listing, Category, User, Wishlist


# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Wishlist)