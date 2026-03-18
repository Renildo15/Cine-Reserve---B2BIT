from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from movie_app.models import Movie

from .serializers import *


@extend_schema(
    request=MovieSerializer,
    description="List movies",
)
class MoviesListView(generics.ListAPIView):
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    queryset = Movie.objects.filter(is_available=True)
