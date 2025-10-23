from django.urls import path
from . import views

app_name = 'vekalet'

urlpatterns = [
    path('dashboard/', views.vekalet_dashboard, name='dashboard'),
]