from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required



from .models import User, Listing, Category, Wishlist
from .forms import CreateForm


def index(request):
    # Check if there's a success message in the session
    success_message = messages.get_messages(request)
    # Pass the success message to the index template
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "success_message": success_message
    })

@login_required
def create(request):
    if request.method == "POST":
        # Store value collected from 'CreateForm' in the form variable or 'None' if no value is collected
        form = CreateForm(request.POST or None)
        if form.is_valid():
            # Save the form data without committing to the database yet
            listing = form.save(commit=False)
            listing.user = request.user.username.capitalize()
            # You might want to associate the listing with the current user
            listing.created_by = request.user  # Assuming you have user authentication
            # Now save the listing to the database
            listing.save()
            form.save_m2m()
            # The form automatically syncs the ManyToManyField, so no further action is needed
            # form.save()
            messages.success(request, "Your form has been submitted successfully")
            return redirect(reverse("index"))
        else:
            messages.error(request, "Please enter correct details")
    else:
        form = CreateForm()
    return render(request, "auctions/create.html", {
        "form" : form,
        "categories": Category.objects.all()
    })


def wishlist(request):

    return render (request, "auctions/wishlist.html")



def listingPage(request, listing_id):
    if request.method == "POST":
        pass
    else:
        # Get the listing to display filtering where the title is the 'listing_title'
        listing_disp = get_object_or_404(Listing, pk=listing_id)
        
        # Retrieve success messages
        success_messages = messages.get_messages(request)

        # Render the template with the listing and success messages
        return render(request, "auctions/listingpage.html", {
            "listing": listing_disp,
            "success_message": success_messages  # Pass success messages to the template
        })


def addwishlist(request, listing_id):
    if request.method == "POST" and request.user.is_authenticated:
        listing = Listing.objects.get(pk=listing_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.listings.add(listing)

        # Wishlist.user = request.user.username
        # Wishlist.listings = request.POST["listing_id"]
        messages.success(request, "Added to wishlist")
        # url = reverse('listingPage', kwargs={'listing_id': listing_id})
        return redirect('listingPage', listing_id=listing_id)




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
