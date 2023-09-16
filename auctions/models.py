from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    id = models.AutoField(primary_key=True)

CATEGORY_CHOICES = [
    ("ELC", "Electronics"),
    ("FSH", "Fashion"),
    ("TYS", "Toys"),
    ("HOM", "Home"),
    ("GRD", "Gardening"),
    ("MSI", "Musical instruments"),
    ("NON", "Other")
]
class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image = models.URLField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default='NON')

    def __str__(self):
        return f"Listing: {self.title}"

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid from {self.user} for listing {self.listing.title} with value: {self.value}"
    

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"comment from {self.user} for listing {self.listing.title}"

class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="Watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watched_users")

    def __str__(self):
        return f"watchlist of listing {self.listing.title } for {self.user}"
    