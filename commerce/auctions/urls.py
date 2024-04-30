from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>", views.listingPage, name="listingPage"),
    path("listing/<int:listing_id>/add_or_remove_watchlist", views.add_or_remove_watchlist, name="add_or_remove_watchlist"),
    path("listing/<int:listing_id>/bid_item", views.bid_item, name="bid_item"),
    path('listing/<int:listing_id>/close/', views.close_listing, name='close_listing'),
    path('listing/<int:listing_id>/addcomment/', views.addcomment, name='addcomment'),
    path("listing_detail/<int:listing_id> ", views.listing_detail, name="listing_detail"),
]

