from django.urls import path

from .views import *

app_name = "sessions"

urlpatterns = [
    path("<int:movie_id>/sessions/", SessionsListView.as_view(), name="sessions_list"),
    path("<int:session_id>/seats/", SessionSeatMapView.as_view(), name="seatmap_list"),
    path("<int:session_id>/reserve/", ReserveSeatView.as_view(), name="reserve"),
    path("<int:session_id>/checkout/", CheckoutView.as_view(), name="checkout"),
]
