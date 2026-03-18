from django.urls import path

from .views import *

app_name = "users"

urlpatterns = [
    path("register", UserRegisterView.as_view(), name="user_register"), 
    path("me/tickers/", MyTicketsView.as_view(), name="me_tickers"),
    path("me/tickers/history/", MyTicketsHistoryView.as_view(), name="me_tickers_history")
]
