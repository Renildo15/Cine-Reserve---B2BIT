from django.contrib.auth.models import User
from django.db import models

from movie_app.models import Movie
from room_app.models import Room, Seat


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="sessions")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField()
    is_available = models.BooleanField(default=False)

    class Meta:
        db_table = "session"
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} {self.start_time}"


class SeatLock(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    locked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "seatlock"
        verbose_name = "Seat Lock"
        verbose_name_plural = "Seats Lock"
        constraints = [
            models.UniqueConstraint(
                fields=["session", "seat"],
                name="unique_seatlock_per_session",
            )
        ]

    def __str__(self):
        return f"{self.session.movie.title} {self.session.start_time} - {self.session.room.name} - {self.seat.row} {self.seat.number} - {self.user.username}"


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    purchased_at = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(unique=True, editable=False)

    class Meta:
        db_table = "ticker"
        verbose_name = "Ticker"
        verbose_name_plural = "Tickers"

    def __str__(self):
        return f"{self.session.movie.title} - {self.session.room.name} {self.session.start_time} - {self.seat.row}{self.seat.number}"
