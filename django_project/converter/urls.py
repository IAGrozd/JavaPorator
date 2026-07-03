from django.urls import path
from . import views

urlpatterns = [
    path('', views.converter_home, name='converter_home'),
    path('register/', views.register, name='register')
]