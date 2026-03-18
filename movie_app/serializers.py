import re

from rest_framework import serializers

from movie_app.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
    )
    description = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    duration = serializers.IntegerField(
        min_value=1,
        max_value=600,
    )
    rating = serializers.CharField(
        max_length=10,
        allow_blank=False,
    )

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "rating",
            "is_available",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_title(self, value):
        sanitized = value.strip()
        if not re.match(r'^[\w\s\-.,!?\'"():;&]+$', sanitized):
            raise serializers.ValidationError("Title contains invalid characters.")
        return sanitized

    def validate_rating(self, value):
        valid_ratings = ["G", "PG", "PG-13", "R", "NC-17", "NR"]
        if value not in valid_ratings:
            raise serializers.ValidationError(
                f"Invalid rating. Must be one of: {', '.join(valid_ratings)}"
            )
        return value
