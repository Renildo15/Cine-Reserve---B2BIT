from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from session_app.models import Ticket
from session_app.serializers import TicketSerializer

from .serializers import *
from .throttling import LoginRateThrottle, RegisterRateThrottle


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle, AnonRateThrottle]


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle, AnonRateThrottle]

    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: UserSerializer},
        description="Register a new user",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BaseTickersView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def base_queryset(self):
        return Ticket.objects.filter(user=self.request.user).select_related(
            "session__movie",
            "session__room",
            "seat"
        )


class MyTicketsView(BaseTickersView):
    @extend_schema(
        responses={200: TicketSerializer(many=True)},
        description="My upcoming tickets",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.base_queryset().filter(session__start_time__gt=now()).order_by("-session__start_time")


class MyTicketsHistoryView(BaseTickersView):
    @extend_schema(
        responses={200: TicketSerializer(many=True)},
        description="My tickets history",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.base_queryset().filter(session__start_time__lte=now()).order_by("-session__start_time")
