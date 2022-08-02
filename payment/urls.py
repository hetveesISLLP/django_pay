from django.urls import path
from .views import home, paymenthandler

urlpatterns = [
    path('', home, name='home'),
    path('paymenthandler/', paymenthandler, name='paymenthandler'),
]