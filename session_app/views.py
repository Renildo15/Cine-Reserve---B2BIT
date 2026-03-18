import uuid

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from helpers.get_lock_key import get_lock_key
from room_app.models import Seat

from .models import Session, Ticket
from .serializers import *


@extend_schema(
    request=SessionSerializer,
    description="List movies",
)
class SessionsListView(generics.ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs.get("movie_id")
        return (
            Session.objects.filter(movie_id=movie_id, is_available=True)
            .select_related("movie", "room")
            .order_by("start_time")
        )


@extend_schema(
    request=SeatMapSerializer,
    description="List Seat Map",
)
class SessionSeatMapView(generics.ListAPIView):
    serializer_class = SeatMapSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        session_id = self.kwargs["session_id"]

        self.session = Session.objects.select_related("room").get(id=session_id)

        return Seat.objects.filter(room=self.session.room)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        tickets = Ticket.objects.filter(session=self.session)
        redis_client = settings.REDIS_CLIENT

        ticket_seat_ids = set(tickets.values_list("seat_id", flat=True))

        keys = redis_client.scan_iter(f"lock:session:{self.session.id}:seat:*")

        locked_seat_ids = {int(key.split(":")[-1]) for key in keys}

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={
                "ticket_seat_ids": ticket_seat_ids,
                "locked_seat_ids": locked_seat_ids,
            },
        )

        return Response(serializer.data)


@extend_schema(
    request=ReserveSeatSerializer,
    description="Reserve Seat",
)
class ReserveSeatView(generics.CreateAPIView):
    serializer_class = ReserveSeatSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        session_id = self.kwargs["session_id"]
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        seat_id = serializer.validated_data["seat_id"]

        session = Session.objects.get(id=session_id)
        seat = Seat.objects.get(id=seat_id)

        if Ticket.objects.filter(session=session, seat=seat).exists():
            raise ValidationError("Seat already purchased")

        redis_client = settings.REDIS_CLIENT
        lock_key = get_lock_key(session_id, seat_id)

        is_locked = redis_client.set(lock_key, user.id, nx=True, ex=600)

        if not is_locked:
            raise ValidationError("Seat is already reserved")

        return Response({"message": "Seat reserved successfully", "expires_in": 600})


@extend_schema(
    request=CheckoutSerializer,
    description="Checkout",
)
class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        session_id = self.kwargs["session_id"]
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        seat_id = serializer.validated_data["seat_id"]

        session = Session.objects.get(id=session_id)
        seat = Seat.objects.get(id=seat_id)

        redis_client = settings.REDIS_CLIENT
        lock_key = get_lock_key(session_id, seat_id)

        lock_owner = redis_client.get(lock_key)

        if not lock_owner:
            raise ValidationError("Lock expired or does not exist")

        if str(lock_owner) != str(user.id):
            raise ValidationError("You do not own this lock")

        if Ticket.objects.filter(session=session, seat=seat).exists():
            raise ValidationError("Seat already purchased")

        with transaction.atomic():
            ticket = Ticket.objects.create(
                user=user, session=session, seat=seat, code=uuid.uuid4()
            )

            redis_client.delete(lock_key)

        return Response(
            {"message": "Ticket purchased successfully", "ticket_id": ticket.id}
        )
