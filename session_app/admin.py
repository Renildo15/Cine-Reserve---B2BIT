from django.contrib import admin

from .models import SeatLock, Session, Ticket


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "room", "start_time")
    list_filter = ("movie", "room")
    search_fields = ("movie__title", "room__name")


@admin.register(SeatLock)
class SeatLockAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "seat", "user", "locked_at", "expires_at")
    list_filter = ("session",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session", "seat", "purchased_at", "code")
    list_filter = ("session",)
    search_fields = ("user__username", "code")
