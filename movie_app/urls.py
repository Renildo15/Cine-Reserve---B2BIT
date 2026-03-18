from django.urls import path

from .views import MoviesListView

app_name = "movies"

urlpatterns = [path("", MoviesListView.as_view(), name="movie_list")]
