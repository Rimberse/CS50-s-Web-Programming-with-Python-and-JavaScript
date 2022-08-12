from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('wiki/<str:entry>', views.page, name='page'),
    path('search', views.search, name='search'),
    path('new', views.add, name='add'),
    path('edit/<str:entry>', views.modify, name='modify'),
    path('random', views.randomize, name='randomize')
]
