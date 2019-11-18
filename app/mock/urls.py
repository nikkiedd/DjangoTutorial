from django.urls import path
from mock import views


urlpatterns = [
path('', views.index, name='index'),
]