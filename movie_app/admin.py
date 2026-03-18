from django.contrib import admin

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "duration", "rating", "created_at")
    search_fields = ("title",)
    list_filter = ("rating",)
