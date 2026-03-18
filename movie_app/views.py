from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from movie_app.models import Movie

from .serializers import *


class MoviesListView(generics.ListAPIView):
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Movie.objects.filter(is_available=True)

    @extend_schema(
        request=MovieSerializer,
        description="List available movies",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
