from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


# Users: tom.ford@example.com, bryan.oconnor@yahoo.com, madelene.ohara@gmail.com, susan.mox@yandex.com
class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.TextField()
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    # auto_now_add - adds timestampt only on object creation, auto_now however adds timestamp each time object is saved with .save() function. Helpful to track edit history of posts
    datetime = models.DateTimeField(auto_now=True)
    likers = models.ManyToManyField(User, blank=True, related_name='likes')

    def __str__(self):
        return f'{self.poster.username} has written: {self.content} in {self.datetime}'


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.follower.username} has followed {self.following.username} in {self.datetime}'