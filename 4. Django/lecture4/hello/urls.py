from django.urls import path
from . import views

# this file defines routes used to access http endpoints

# empty string represents no additional route (nothing at the end of the route)
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:name>', views.greet, name='greet'),
    path('kerim', views.kerim, name='kerim'),
    path('david', views.david, name='david')
]