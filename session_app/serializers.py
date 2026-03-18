from rest_framework import serializers

from room_app.models import Seat

from .models import Session, Ticket


class SessionSerializer(serializers.ModelSerializer):
    movie_name = serializers.CharField(source="movie.title", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Session
        fields = ["id", "movie_name", "room_name", "start_time"]
        read_only_fields = ["id", "movie_name", "room_name"]


class SeatMapSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["row", "number", "status"]

    def get_status(self, obj):
        ticket_seat_ids = self.context.get("ticket_seat_ids", set())
        locked_seat_ids = self.context.get("locked_seat_ids", set())

        if obj.id in ticket_seat_ids:
            return "purchased"
        elif obj.id in locked_seat_ids:
            return "reserved"
        return "available"


class ReserveSeatSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField(
        min_value=1,
        help_text="ID of the seat to reserve"
    )

    def validate_seat_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Invalid seat ID")
        return value


class CheckoutSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField(
        min_value=1,
        help_text="ID of the seat to purchase"
    )

    def validate_seat_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Invalid seat ID")
        return value


class TicketSerializer(serializers.ModelSerializer):
    movie = serializers.CharField(source="session.movie.title", read_only=True)
    start_time = serializers.DateTimeField(source="session.start_time", read_only=True)
    room = serializers.CharField(source="session.room.name", read_only=True)
    seat = serializers.SerializerMethodField(read_only=True)

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
