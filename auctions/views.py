from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, TextInput, URLInput, Textarea, NumberInput, Select
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages



def get_watchlist(request):
    if request.user.is_authenticated:
        return request.user.Watchlist.all()
    else:
        return None

def index(request):
    listings = Listing.objects.filter(available=True)
    max_bids_values = []
    for l in listings:
        if l.bids.values_list('value'):
            max_bids_values.append(max(l.bids.values_list('value'))[0])
        else:
            max_bids_values.append("no bids")
    listings_dict = dict(zip(listings, max_bids_values))
    return render(request, "auctions/index.html", {
        "listings": listings_dict,
        "user_watchlist" : get_watchlist(request)
    })

@login_required(login_url='/login')
def watchlist(request):
    watchlist_listings = request.user.Watchlist.all()
    listings = []
    max_bids_values = []
    for l in watchlist_listings:
        if l.listing.bids.values_list('value'):
            max_bids_values.append(max(l.listing.bids.values_list('value'))[0])
        else:
            max_bids_values.append("no bids")
        listings.append(l.listing)
    listings_dict = dict(zip(listings, max_bids_values))
    return render(request, "auctions/watchlist.html", {
        "listings": listings_dict,
        "user_watchlist" : get_watchlist(request)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS ,'login successfully!', extra_tags='success login')
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("auctions:index"))
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS ,'You have successfully logged out!', extra_tags='success login')
    return HttpResponseRedirect(reverse("auctions:index"))


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
        messages.add_message(request, messages.SUCCESS ,'You have registered successfully!', extra_tags='success login')
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")



class Create_form(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': TextInput(attrs={'placeholder': 'Title', 'style': 'width: 300px;', 'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'style': 'width: 700px;'}),
            'starting_bid': NumberInput(attrs={'class': 'form-control', 'style': 'width: 150px;'}),
            'image': URLInput(attrs={'class': 'form-control', 'style': 'width: 700px;', 'placeholder': "optional"}),
            'category': Select(attrs={'class': 'form-control', 'style': 'width: 300px;'})
        }


@login_required(login_url='/login')
def create(request):
    if request.method == "POST":
        f = Create_form(request.POST)
        if f.is_valid():
            l = f.save(commit=False)
            l.user = request.user
            try:
                l.save()
            except IntegrityError:
                return render(request, "auctions/create.html", {
                    "create_form": Create_form(request.POST),
                    "message": "Title is dublicated, Please choose another title",
                    "user_watchlist" : get_watchlist(request)
                })
        messages.add_message(request, messages.SUCCESS ,'You have created a new listing!', extra_tags='success created')
        return HttpResponseRedirect(reverse("auctions:listing", args=[l.id]))
    else:
        return render(request, "auctions/create.html", {
            "create_form": Create_form(),
            "user_watchlist" : get_watchlist(request)
        })



def listing(request, id):
    watchlist_flag = True if request.user.is_authenticated and Watchlist.objects.filter(listing=id, user=request.user) else False
    author_flag = True if request.user == Listing.objects.get(pk=id).user else False
    available_flag =  Listing.objects.get(pk=id).available
    comments = Listing.objects.get(pk=id).comments.all()
    if Bid.objects.filter(listing=id):
        max_bid = Bid.objects.filter(listing=id).order_by('-value').first()
        max_bid_current_user_flg = True if request.user == max_bid.user else False
        minimum_bid = max_bid.value + 1 
    else:
        max_bid_current_user_flg = False
        max_bid = "no bids"
        minimum_bid = Listing.objects.get(pk=id).starting_bid

    if request.method == "POST":
        if request.POST.get("bid_value"):
            if int(request.POST["bid_value"]) >= minimum_bid:
                b = Bid(user=request.user, listing=Listing.objects.get(pk=id), value=request.POST["bid_value"])
                b.save()
                messages.add_message(request, messages.SUCCESS ,'Your bid was added', extra_tags='success bid')
                return HttpResponseRedirect(reverse("auctions:listing", args=[id]))
        elif request.POST.get("add_watchlist"):
            w = Watchlist(user=request.user, listing=Listing.objects.get(pk=id))
            w.save()
            messages.add_message(request, messages.SUCCESS ,'Added to watchlist', extra_tags='success watchlist')
            return HttpResponseRedirect(reverse("auctions:listing", args=[id]))
        elif request.POST.get("rmv_watchlist"):
            w = Watchlist.objects.get(listing=id, user=request.user)
            w.delete()
            messages.add_message(request, messages.SUCCESS ,'Removed from watchlist', extra_tags='success watchlist')
            return HttpResponseRedirect(reverse("auctions:listing", args=[id]))
        elif request.POST.get('close_auction'):
            l = Listing.objects.get(pk=id)
            l.available = False
            l.save()
            messages.add_message(request, messages.SUCCESS ,'Auction closed', extra_tags='success closed')
            return HttpResponseRedirect(reverse("auctions:listing", args=[id]))
        elif request.POST.get('comment'):
            comment = request.POST.get('comment')
            c = Comment(listing=Listing.objects.get(pk=id), user=request.user, text=comment)
            c.save()
            messages.add_message(request, messages.SUCCESS ,'Comment added', extra_tags='success comment')
            return HttpResponseRedirect(reverse("auctions:listing", args=[id]))
        else:
            return HttpResponseRedirect(reverse("auctions:listing", args=[id]))
    else:
        return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(pk=id),
                "max_bid": max_bid  ,
                "num_bids": len(Bid.objects.filter(listing=id)),
                "max_bid_current_user_flg": max_bid_current_user_flg,
                "minimum_bid": minimum_bid,
                "watchlist_flag": watchlist_flag,
                "user_watchlist" : get_watchlist(request),
                "author_flag": author_flag,
                "available_flag": available_flag,
                "comments": comments
            })


def category(request):
    return render(request, "auctions/category.html", {
        "CATEGORY_CHOICES":CATEGORY_CHOICES,
        "user_watchlist" : get_watchlist(request)
        
        })

def specific_category(request, category):
    all_lisitngs_in_category = Listing.objects.filter(category=category, available=True)
    human_category = [cat[1] for cat in CATEGORY_CHOICES if category == cat[0]][0]
    max_bids_values = []
    for l in all_lisitngs_in_category:
        if l.bids.values_list('value'):
            max_bids_values.append(max(l.bids.values_list('value'))[0])
        else:
            max_bids_values.append("no bids")
    listings_dict = dict(zip(all_lisitngs_in_category, max_bids_values))

    return render(request, "auctions/specific_category.html", {
        "all_lisitngs_in_category":listings_dict,
        "human_category": human_category,
        "user_watchlist" : get_watchlist(request)
        })