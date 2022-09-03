from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import logging

from .models import User, Listing, Bid, Comment, Watchlist, Archive


# Main page, used to see active listings
def index(request):
    logging.debug(Listing.objects.all())
    return render(request, "auctions/index.html", {
        # Exclude listing that are archived
        'listings': Listing.objects.exclude(pk__in=Archive.objects.all())
    })


# Used to see all categories of active listings
def categories(request):
    return render(request, "auctions/categories.html", {
        'categories': list(map(lambda category: category[1], Listing.CATEGORIES))
    })


# Used too see all the listings contained within a specific category
def category(request, category_name):
    # Find all listing associated within given category
    listings = list(filter(lambda element: element.category == category_name, Listing.objects.all()))
    logging.debug(f'Listings in {category_name} category: {listings}')

    return render(request, 'auctions/category.html', {
        'name': category_name,
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            # Load watchlist contents count
            request.session['watchlist_count'] = Watchlist.objects.filter(creator=user).all().count()

            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
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


# Used to view a specific listing
def listing(request, listing_id):
    listing = Listing.objects.get(pk=int(listing_id))
    logging.debug(f'Associated listing with a requested id {listing_id}: {listing}')
    
    # Case 1: Listing is no longer active and has been archived
    # In this case it's no longer possible to place bids, hence user can only see the winner
    try:
        archived_listing = Archive.objects.get(pk=listing_id)
        logging.debug(f'An archived listing has been found: {archived_listing}')

        return render(request, 'auctions/listing.html', {
            'listing': archived_listing.listing,
            'winner': archived_listing.winner
        })
    # Case 2: Listing is still active
    # In this case it's still possible to place bids
    except ObjectDoesNotExist:
        # Retrieve total amounts of bids current placed by all clients for all listings
        total_bids = Bid.objects.values('listing').annotate(bids=Count('pk')).order_by('listing')
        # Filter out listings to only count number bids for the current listings
        listing_bids = list(filter(lambda element: element['listing'] == listing_id, total_bids))
        logging.debug(f'Listing contains {listing_bids} bids')

        bids = Bid.objects.filter(listing=listing).values()
    
        # Pass number of bids for this listing in the context if current placements were found, if not pass 0
        # Also pass starting bid, which can't be lower than the highest bid, if no bids have been placed, it should be at least equal to the starting bid listed by the creator
        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'bids': listing_bids[0]['bids'] if listing_bids else 0,
            'starting_bid': float(max(bids, key=lambda element: element['price'])['price']) + 1 if bids else listing.price
        })


# Used to add the items to the watchlist
@login_required
def watch(request):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=int(request.POST['listing_id']))
        user = User.objects.get(pk=int(request.POST['user_id']))

        logging.debug(f'Listing: {listing}')
        logging.debug(f'Creator: {user}')

        watchlist = Watchlist.objects.filter(creator=user, listing=listing)

        # if the listing is already on watchlist, remove it
        if watchlist:
            watchlist.delete()
        # else add listing to watchlist
        else:
            watchlist = Watchlist(creator=user, listing=listing)
            watchlist.save()
            logging.info(Watchlist.objects.filter(creator=user).all())

        # Storing watchlist count in session makes it globally available, even in a template
        request.session['watchlist_count'] = Watchlist.objects.filter(creator=user).all().count()
        return HttpResponseRedirect(reverse('listings', args=(listing.id, )))


# Used to see listing in user's watchlist
@login_required
def watchlist(request, user_id):
    user = User.objects.get(pk=int(user_id))

    # Find ids of listing contained in user's watchlist
    listing_ids = Watchlist.objects.filter(creator=user).all().values_list('listing', flat=True)

    # if user's watchlist is not empty
    if listing_ids:
        # Find all listing instances associated with these ids by filtering out objects in Listing model
        listings = list(filter(lambda element: element.id in listing_ids, Listing.objects.all()))
        logging.info(f'Listings in watchlist: {listings}')

        return render(request, 'auctions/watchlist.html', {
            'listings': listings
        })
    # else warn the user with a message
    else:
        return render(request, 'auctions/watchlist.html', {
            'message': 'Your watchlist is empty. You haven\'t added anything into it yet!',
            'listings': None
        })


# Used to place bids
@login_required
def bid(request):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=int(request.POST['listing_id']))
        price = request.POST['bid']
        bidder = User.objects.get(pk=int(request.POST['user_id']))

        logging.debug(f'Listing: {listing}')
        logging.debug(f'Bid: {price}')
        logging.debug(f'Bidder: {bidder}')

        # Check if the listing creator tries to place a bid, in which case prevent it from happening
        if listing.owner.id == bidder.id:
            return render(request, 'auctions/listing.html', {
                'message': 'Listing creators can\'t place bids for their own listings',
                'listing': listing
            })
        else:
            bid = Bid.objects.create(listing=listing, price=price, bidder=bidder)
            bid.save()
            return HttpResponseRedirect(reverse("index"))


# Used to leave comments
@login_required
def comment(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=int(listing_id))
        text = request.POST['text']
        author = User.objects.get(pk=int(request.POST['user_id']))

        logging.debug(f'Listing: {listing}')
        logging.debug(f'Text: {text}')
        logging.debug(f'Author: {author}')

        # If this comment doesn't already exist, find an associated listing and add a comment into it's comments section
        try:
            comment = Comment.objects.create(text=text, author=author)
            comment.save()
            listing.comments.add(comment)

            return HttpResponseRedirect(reverse('listings', args=(listing_id, )))
        # Duplicate comments are forbidden. In detected, inform the user
        except IntegrityError:
            return render(request, 'auctions/listing.html', {
                'message': 'This comment already exists. Comments should be unique',
                'listing': listing
            })


# Used to create new listing to place them in auction as an active listing
@login_required
def create(request):
    if request.method == 'POST':
        user = User.objects.get(pk=int(request.POST["user_id"]))
        title = request.POST['title']
        description = request.POST['description']
        price = float(request.POST['price'])
        image = request.POST['image']
        category = request.POST['category']
    
        # Logging passed as a parameter payload:
        logging.debug('POST request parameters:')
        logging.debug(f'User id: {user}')
        logging.debug(f'Title: {title}')
        logging.debug(f'Description: {description}')
        logging.debug(f'Starting bid: {price}')
        logging.debug(f'URL of image: {image}')
        logging.debug(f'Category: {category}')

        try:
            listing = Listing.objects.create(title=title, description=description, price=price, image=image, category=category, owner=user)
            logging.debug(f'Listing: {listing}')
            listing.save()
        except IntegrityError:
            return render(request, 'auctions/create_listing.html', {
                'message': 'Listing already exists.'
            })
        return HttpResponseRedirect(reverse('index'))   
    else:
        # Extract 2nd element from array of tuples and return them as list
        return render(request, 'auctions/create_listing.html', {
            'categories': list(map(lambda category: category[1], Listing.CATEGORIES))
        })


# Used  to close the auction and select the winner
@login_required
def close(request):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=int(request.POST['listing_id']))
        lister = User.objects.get(pk=int(request.POST['user_id']))

        logging.debug(f'Listing: {listing}')
        logging.debug(f'Lister: {lister}')

        # Find all bids associated with this listing
        bids = Bid.objects.filter(listing=listing).values()
        logging.debug(f'Bids: {bids}')

        # If there were no bids places, no action is necessary
        # Else find out the winner and inform them about victory
        if bids:
            # Find a bid with the highest value -> find the winner of the auction
            highest_bid = max(bids, key=lambda element: element['price'])
            logging.debug(f'Highest bid: {highest_bid}')
            winner = User.objects.get(pk=highest_bid['bidder_id'])
            logging.debug(f'Winner of the auction: {winner}')

            # Archive an item
            archived_listing = Archive.objects.create(id=listing.id, listing=listing, winner=winner)
            archived_listing.save()
        
        # Remove item from active listing
        listing.pk = None
        # listing.save()

        return HttpResponseRedirect(reverse('index'))   
