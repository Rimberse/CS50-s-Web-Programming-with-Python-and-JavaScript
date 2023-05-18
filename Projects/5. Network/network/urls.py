
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.post, name="post"),
    path("posts/like", views.like, name="like"),
    path("posts/edit/<int:post_id>", views.edit, name="edit"),
    path("posts/page/<int:page_number>", views.load_page, name="load_page"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("following/posts/page/<int:page_number>", views.following, name="following")
]
