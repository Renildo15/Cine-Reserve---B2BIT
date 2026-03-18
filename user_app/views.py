from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import *
from session_app.serializers import TicketSerializer
from session_app.models import Ticket

# Create your views here.


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: UserSerializer},
        description="Register a new user",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

from django.utils.timezone import now


class BaseTickersView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def base_queryset(self):
        return Ticket.objects.filter(user=self.request.user).select_related(
            "session__movie",
            "session__room",
            "seat"
        )
@extend_schema(
    responses={200: TicketSerializer(many=True)},
    description="My tickers",
)
class MyTicketsView(BaseTickersView):

    def get_queryset(self):
        return self.base_queryset().filter(session__start_time__gt=now()).order_by("-session__start_time")

@extend_schema(
    responses={200: TicketSerializer(many=True)},
    description="My tickers history",
)
class MyTicketsHistoryView(BaseTickersView):

    def get_queryset(self):
        return self.base_queryset().filter(session__start_time__lte=now()).order_by("-session__start_time")
