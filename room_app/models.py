from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    total_rows = models.IntegerField()
    seats_per_row = models.IntegerField()

    class Meta:
        db_table = "room"
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.name}"


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    row = models.CharField(max_length=5)
    number = models.IntegerField()

    class Meta:
        db_table = "seat"
        verbose_name = "Seat"
        verbose_name_plural = "Seats"
        unique_together = ("room", "row", "number")
        constraints = [
            models.UniqueConstraint(
                fields=["room", "row", "number"],
                name="unique_seat_per_room",
            )
        ]

    def __str__(self):
        return f"{self.room.name} - {self.row} {self.number}"
