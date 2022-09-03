from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create', views.create, name='create'),
    path('listings/<int:listing_id>', views.listing, name='listings'),
    path('place_bid', views.bid, name='bid'),
    path('close_auction', views.close, name='close'),
    path('add_to_watchlist', views.watch, name='watch'),
    path('watchlists/<int:user_id>', views.watchlist, name='watchlists'),
    path('<int:listing_id>/comment', views.comment, name='comment'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category_name>', views.category, name='category')
]
