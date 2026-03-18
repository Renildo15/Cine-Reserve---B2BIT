from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from movie_app.models import Movie
from movie_app.serializers import MovieSerializer


class MovieModelTest(TestCase):
    def test_create_movie(self):
        movie = Movie.objects.create(
            title="Inception",
            description="A thief who steals corporate secrets",
            duration=148,
            rating="PG-13",
            is_available=True,
        )
        self.assertEqual(str(movie), "Inception - PG-13")
        self.assertEqual(movie.title, "Inception")
        self.assertEqual(movie.duration, 148)
        self.assertTrue(movie.is_available)

    def test_movie_default_values(self):
        movie = Movie.objects.create(
            title="Test Movie",
            description="Test description",
            duration=120,
            rating="G",
        )
        self.assertFalse(movie.is_available)
        self.assertIsNotNone(movie.created_at)

    def test_movie_ordering(self):
        Movie.objects.all().delete()
        movie1 = Movie.objects.create(title="First", description="d", duration=60, rating="G")
        movie2 = Movie.objects.create(title="Second", description="d", duration=60, rating="G")
        movies = list(Movie.objects.all())
        self.assertEqual(movies[0].title, "Second")
        self.assertEqual(movies[1].title, "First")


class MovieSerializerTest(TestCase):
    def test_serializer_contains_expected_fields(self):
        movie = Movie.objects.create(
            title="Matrix",
            description="A hacker discovers reality",
            duration=136,
            rating="R",
            is_available=True,
        )
        serializer = MovieSerializer(movie)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "description", "duration", "rating", "is_available", "created_at"},
        )

    def test_serializer_valid_data(self):
        data = {
            "title": "Test Movie",
            "description": "Test description",
            "duration": 120,
            "rating": "PG",
            "is_available": True,
        }
        serializer = MovieSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_missing_title(self):
        data = {
            "description": "Test description",
            "duration": 120,
            "rating": "PG",
        }
        serializer = MovieSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)


class MoviesListViewTest(APITestCase):
    def setUp(self):
        Movie.objects.all().delete()
        self.movie1 = Movie.objects.create(
            title="Available Movie",
            description="This movie is available",
            duration=120,
            rating="PG",
            is_available=True,
        )
        self.movie2 = Movie.objects.create(
            title="Unavailable Movie",
            description="This movie is not available",
            duration=90,
            rating="G",
            is_available=False,
        )

    def test_list_only_available_movies(self):
        url = reverse("movies:movie_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movies = response.data["results"]
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0]["title"], "Available Movie")

    def test_list_movies_contains_expected_fields(self):
        url = reverse("movies:movie_list")
        response = self.client.get(url)
        movie_data = response.data["results"][0]
        self.assertIn("id", movie_data)
        self.assertIn("title", movie_data)
        self.assertIn("description", movie_data)
        self.assertIn("duration", movie_data)
        self.assertIn("rating", movie_data)
        self.assertIn("is_available", movie_data)
        self.assertIn("created_at", movie_data)

    def test_list_movies_empty(self):
        Movie.objects.all().delete()
        url = reverse("movies:movie_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_movies_ordered_by_created_at_desc(self):
        Movie.objects.all().delete()
        movie1 = Movie.objects.create(
            title="First Movie", description="d", duration=60, rating="G", is_available=True
        )
        movie2 = Movie.objects.create(
            title="Second Movie", description="d", duration=60, rating="G", is_available=True
        )
        url = reverse("movies:movie_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movies = response.data["results"]
        self.assertEqual(len(movies), 2)
        self.assertEqual(movies[0]["title"], "Second Movie")
        self.assertEqual(movies[1]["title"], "First Movie")

    def test_response_has_pagination_fields(self):
        url = reverse("movies:movie_list")
        response = self.client.get(url)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
