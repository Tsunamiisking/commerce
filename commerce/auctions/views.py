from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required



from .models import User, Listing, Category, Watchlist, Bid, Comment
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
            messages.success(request, "Your listing has been created successfully")
            return redirect(reverse("index"))
        else:
            messages.error(request, "Please enter correct details")
    else:
        form = CreateForm()
    return render(request, "auctions/create.html", {
        "form" : form,
        "categories": Category.objects.all()
    })


# def watchlist(request):
#     listings = watchlist.objects.filter(user=request.user)
#     return render (request, "auctions/watchlist.html", {
#        "listings" : listings 
#     })

def watchlist(request):
    # Assuming the user is logged in, get the current user's watchlist
    if request.user.is_authenticated:
        watchlist_items = Watchlist.objects.filter(user=request.user)
        listings = []
        bids = Bid.objects.filter(user=request.user)
        # Iterate over each watchlist item and get its associated listings
        for watchlist_item in watchlist_items:
            listings.extend(watchlist_item.listings.all())
        
    else:
        # If the user is not logged in, handle it as per your requirements
        listings = []  # Or you can redirect to a login page, etc.

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "Bids" : bids,
        })

def categoryDisp(request):
    categories = Category.objects.all()

    return render(request, "auctions/category.html", {
        "categories" : categories,
    })

def category(request, category_id):
    category_to_search = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(item_category=category_to_search)

    return render(request, "auctions/categorygroup.html", {
        "listings" : listings,
        "category_to_search" : category_to_search
    })

def listingPage(request, listing_id):
    # Get the listing to display
    listing_disp = get_object_or_404(Listing, pk=listing_id)
    current_user = request.user

    # Check if the listing is in the user's watchlist
    is_in_watchlist = checklisting(current_user, listing_disp.id)

    # Determine the button text based on whether the listing is in the watchlist
    button_text = "Add to watchlist" if not is_in_watchlist else "Remove from watchlist"
    comments = Comment.objects.filter(listing=listing_disp)
    # Retrieve success messages
    success_messages = messages.get_messages(request)
    if get_highest_bidder(listing_id) == request.user.username and listing_disp.is_closed:
        success_message  = "Congratulations!! Listing closed You Won the auction"
        messages.success(request, success_message) 
    # Render the template with the listing and success messages
    return render(request, "auctions/listingpage.html", {
        "listing": listing_disp,
        "messages": success_messages,  # Pass success messages to the template
        "button": button_text,
        "comments" : comments
    })

def addcomment(request, listing_id):
    if request.method == "POST":
        comment_text = request.POST["comment-text"]
        listing = Listing.objects.get(pk=listing_id)
        new_comment = Comment()

        new_comment.listing = listing
        new_comment.user = request.user.username
        new_comment.text = comment_text

        new_comment.save()

        return redirect('listingPage', listing_id=listing_id)

        
    

# def checklisting(listing_id):
#     listing = Listing.objects.get(pk=listing_id).id
#     watchlist_listing = watchlist.objects.all()
#     if listing in watchlist_listing.listings.id:
#         return True
#     else:
#         return False


def checklisting(user, listing_id):
    try:
        # Check if the listing exists in the current user's watchlist
        watchlist_item = Watchlist.objects.get(user=user, listings__id=listing_id).id
        return True
    except Watchlist.DoesNotExist:
        return False

@login_required
def add_or_remove_watchlist(request, listing_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            listing = Listing.objects.get(pk=listing_id)
            watchlist, created = Watchlist.objects.get_or_create(user=request.user)
            # Check if the listing is already in the user's watchlist
            if listing in watchlist.listings.all():
                # If the listing is already in the watchlist, remove it
                watchlist.listings.remove(listing)
                message = "Removed from watchlist"
            else:
                # If the listing is not in the watchlist, add it
                watchlist.listings.add(listing)
                message = "Added to watchlist"
            messages.success(request, message)
            # Redirect to the listing page with the appropriate message
            return redirect(reverse("listingPage", kwargs={'listing_id': listing_id}))


        else:
            messages.error(request, 'Please login')
            return HttpResponseRedirect(reverse('login'))
    else:
        # Handle the case where the request method is not POST
        return HttpResponseRedirect(reverse("index"))

def bid_item(request, listing_id):
    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        listing = get_object_or_404(Listing, pk=listing_id)
        original_amount = listing.price

        if not bid_amount:
            messages.error(request, "Bid amount cannot be empty.")
            return redirect(reverse("index"))

        bid_amount = float(bid_amount)

        if bid_amount <= original_amount:
            messages.error(request, "Bid amount must be higher than the current price.")
            return redirect(reverse("index"))

        # Check if the bid is higher than any previous bid
        previous_bids = Bid.objects.filter(listing=listing)
        if previous_bids.exists() and bid_amount <= previous_bids.order_by("-amount").first().amount:
            messages.error(request, "Bid amount must be higher than any previous bid.")
            return redirect(reverse("index"))

        # Create and save the bid object
        bid = Bid.objects.create(user=request.user, listing=listing, amount=bid_amount)
        messages.success(request, "Bid placed successfully.")
        return redirect(reverse("index"))

    else:
        # Handle GET request if needed
        return redirect(reverse("index"))

def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    # Check if the user is the owner of the listing
    if request.user.username  == listing.user:
        listing.is_closed = True
        listing.save()
        messages.success(request, "Listing closed successfully.")

    else:
        messages.error(request, "You are not authorized to close this listing.")

    return redirect('listing_detail', listing_id=listing_id)

def get_highest_bidder(listing_id):
    # Get the listing object
    listing = get_object_or_404(Listing, pk=listing_id)

    # Get the highest bid for the listing
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

    if highest_bid:
        # Return the user associated with the highest bid
        return highest_bid.user
    else:
        # No bids found for the listing
        return None
        
def listing_detail(request, listing_id):
    # Get the highest bidder for the listing
    highest_bidder = get_highest_bidder(listing_id)

    return render(request, 'auctions/listing_details.html', {'highest_bidder': highest_bidder})

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
        login_messages = messages.get_messages(request)
        return render(request, "auctions/login.html", {
            "messages": login_messages  # Pass success messages to the template
        })


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
