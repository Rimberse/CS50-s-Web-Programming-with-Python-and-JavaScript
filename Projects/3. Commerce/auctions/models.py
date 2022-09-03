from tkinter import CASCADE
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


class User(AbstractUser):
    pass


class Comment(models.Model):
    text = models.TextField(max_length=1024)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authors')                                           # Many to one

    class Meta:
        unique_together = ["text", "author"]

    def __str__(self):
        return f'Comment: {self.text} by: {self.author}'

class Listing(models.Model):
    # Acts like a select box with a predefined list of choices
    CATEGORIES = [
        ('NO', 'No Category'),
        ('FS', 'Fashion'), 
        ('TY', 'Toys'),
        ('ET', 'Electronics'), 
        ('HM', 'Home'),
        ('MI', 'Magic Item'),
        ('VH', 'Vehicle'),
    ]

    title = models.CharField(max_length=64)
    # Making a field optional in Django models, using blank=True and providing default value:
    image = models.CharField(max_length=1024, blank=True, default='')
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    description = models.TextField(max_length=256)
    date = models.DateTimeField(default=datetime.datetime.now, help_text='Format is: mm-dd-yyyy hh:mm:ss')
    category = models.CharField(max_length=64, choices=CATEGORIES, default='NO')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owners')                                             # Many to one
    comments = models.ManyToManyField(Comment, blank=True, related_name='comments')                                              # Many to many

    # Way to specify uniqueness of table columns (fields). 
    # In this case the same item could be listed multiple times, as long as the owners are different (just like in any other e-commerce website: Amazon, Ebay, Aliexpress)
    class Meta:
        unique_together = ["title", "image", "price", 'description', 'category', 'owner']

    def __str__(self):
        return f'{self.image} {self.title} Starting bid: ${self.price} Description: {self.description} Created {self.date} Category: {self.category} by: {self.owner}. Comments {self.comments}'


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='active_listings')                               # One to many
    price = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bidders')                                           # Many to one

    def __str__(self):
        return f'Listing: {self.listing} ${self.price} bid(s) so far. Your bid is the current bid. Details Listed by: {self.bidder}'


class Watchlist(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creators')                                         # One to one
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing')                                       # One to many

    class Meta:
        unique_together = ["creator", 'listing']

    def __str__(self):
        return f'{self.creator}\'s Watchlist: {self.listing}'


class Archive(models.Model):
    id = models.IntegerField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='auction_listings')                              # One to  many
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winners')                                           # One to many

    class Meta:
        unique_together = ["id"]

    def __str__(self):
        return f'{self.listing}\'s winner: {self.winner}'