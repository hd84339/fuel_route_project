from django.urls import path
from .views import route_api_view

urlpatterns = [
    path('route/', route_api_view),
]