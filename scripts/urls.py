# Assuming you're in an app's `urls.py` file
from django.urls import path
from . import views
from .scripts import views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
]
