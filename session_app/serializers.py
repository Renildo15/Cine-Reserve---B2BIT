from rest_framework import serializers

from room_app.models import Seat

from .models import Session, Ticket


class SessionSerializer(serializers.ModelSerializer):
    movie_name = serializers.CharField(source="movie.title")
    room_name = serializers.CharField(source="room.name")

    class Meta:
        model = Session
        fields = ["id", "movie_name", "room_name", "start_time"]


class SeatMapSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["row", "number", "status"]

    def get_status(self, obj):
        ticket_seat_ids = self.context["ticket_seat_ids"]
        locked_seat_ids = self.context["locked_seat_ids"]

        if obj.id in ticket_seat_ids:
            return "purchased"
        elif obj.id in locked_seat_ids:
            return "reserved"
        return "available"


class ReserveSeatSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField()


class CheckoutSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField()


class TicketSerializer(serializers.ModelSerializer):
    movie = serializers.CharField(source="session.movie.title")
    start_time = serializers.DateTimeField(source="session.start_time")
    room = serializers.CharField(source="session.room.name")
    seat = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "code",
            "movie",
            "start_time",
            "room",
            "seat"
        ]

    def get_seat(self, obj):
        return f"F{obj.seat.row}-A{obj.seat.number}"