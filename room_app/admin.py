from django.contrib import admin

from .models import Room, Seat


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "total_rows", "seats_per_row")
    search_fields = ("name",)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "row", "number")
    list_filter = ("room",)
    search_fields = ("room__name",)
