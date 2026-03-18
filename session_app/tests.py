import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from movie_app.models import Movie
from room_app.models import Room, Seat
from session_app.models import Session, Ticket
from session_app.serializers import (
    CheckoutSerializer,
    ReserveSeatSerializer,
    SeatMapSerializer,
    SessionSerializer,
    TicketSerializer,
)


class SessionModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test",
            duration=120,
            rating="PG",
            is_available=True,
        )
        self.room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)

    def test_create_session(self):
        start_time = timezone.now() + timedelta(days=1)
        session = Session.objects.create(
            movie=self.movie, room=self.room, start_time=start_time, is_available=True
        )
        self.assertEqual(str(session), f"Test Movie - Sala 1 {start_time}")
        self.assertEqual(session.movie, self.movie)
        self.assertEqual(session.room, self.room)
        self.assertTrue(session.is_available)

    def test_session_default_is_available(self):
        start_time = timezone.now() + timedelta(days=1)
        session = Session.objects.create(movie=self.movie, room=self.room, start_time=start_time)
        self.assertFalse(session.is_available)

    def test_session_cascade_delete_movie(self):
        start_time = timezone.now() + timedelta(days=1)
        session = Session.objects.create(movie=self.movie, room=self.room, start_time=start_time)
        session_id = session.id
        self.movie.delete()
        self.assertFalse(Session.objects.filter(id=session_id).exists())

    def test_session_cascade_delete_room(self):
        start_time = timezone.now() + timedelta(days=1)
        session = Session.objects.create(movie=self.movie, room=self.room, start_time=start_time)
        session_id = session.id
        self.room.delete()
        self.assertFalse(Session.objects.filter(id=session_id).exists())


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test",
            duration=120,
            rating="PG",
            is_available=True,
        )
        self.room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)
        self.seat = Seat.objects.create(room=self.room, row="A", number=1)
        start_time = timezone.now() + timedelta(days=1)
        self.session = Session.objects.create(
            movie=self.movie, room=self.room, start_time=start_time, is_available=True
        )

    def test_create_ticket(self):
        ticket = Ticket.objects.create(
            user=self.user, session=self.session, seat=self.seat, code=uuid.uuid4()
        )
        self.assertEqual(str(ticket), f"Test Movie - Sala 1 {self.session.start_time} - A1")
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.session, self.session)
        self.assertEqual(ticket.seat, self.seat)
        self.assertIsNotNone(ticket.code)
        self.assertIsInstance(ticket.code, uuid.UUID)

    def test_ticket_unique_code(self):
        ticket1 = Ticket.objects.create(
            user=self.user, session=self.session, seat=self.seat, code=uuid.uuid4()
        )
        seat2 = Seat.objects.create(room=self.room, row="A", number=2)
        ticket2 = Ticket.objects.create(
            user=self.user, session=self.session, seat=seat2, code=uuid.uuid4()
        )
        self.assertNotEqual(ticket1.code, ticket2.code)

    def test_ticket_cascade_delete_user(self):
        ticket = Ticket.objects.create(
            user=self.user, session=self.session, seat=self.seat, code=uuid.uuid4()
        )
        ticket_id = ticket.id
        self.user.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())

    def test_ticket_cascade_delete_session(self):
        ticket = Ticket.objects.create(
            user=self.user, session=self.session, seat=self.seat, code=uuid.uuid4()
        )
        ticket_id = ticket.id
        self.session.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())

    def test_ticket_cascade_delete_seat(self):
        ticket = Ticket.objects.create(
            user=self.user, session=self.session, seat=self.seat, code=uuid.uuid4()
        )
        ticket_id = ticket.id
        self.seat.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())


class SessionSerializerTest(TestCase):
    def test_contains_expected_fields(self):
        movie = Movie.objects.create(
            title="Matrix", description="Test", duration=136, rating="R", is_available=True
        )
        room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)
        start_time = timezone.now() + timedelta(days=1)
        session = Session.objects.create(movie=movie, room=room, start_time=start_time)
        serializer = SessionSerializer(session)
        data = serializer.data
        self.assertEqual(set(data.keys()), {"id", "movie_name", "room_name", "start_time"})

    def test_movie_name_from_related(self):
        movie = Movie.objects.create(
            title="Inception", description="Test", duration=148, rating="PG-13", is_available=True
        )
        room = Room.objects.create(name="Sala VIP", total_rows=3, seats_per_row=8)
        start_time = timezone.now() + timedelta(days=1)
        session = Session.objects.create(movie=movie, room=room, start_time=start_time)
        serializer = SessionSerializer(session)
        self.assertEqual(serializer.data["movie_name"], "Inception")
        self.assertEqual(serializer.data["room_name"], "Sala VIP")


class SeatMapSerializerTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)
        self.seat1 = Seat.objects.create(room=self.room, row="A", number=1)
        self.seat2 = Seat.objects.create(room=self.room, row="A", number=2)

    def test_status_available(self):
        context = {"ticket_seat_ids": set(), "locked_seat_ids": set()}
        serializer = SeatMapSerializer(self.seat1, context=context)
        self.assertEqual(serializer.data["status"], "available")

    def test_status_purchased(self):
        context = {"ticket_seat_ids": {self.seat1.id}, "locked_seat_ids": set()}
        serializer = SeatMapSerializer(self.seat1, context=context)
        self.assertEqual(serializer.data["status"], "purchased")

    def test_status_reserved(self):
        context = {"ticket_seat_ids": set(), "locked_seat_ids": {self.seat1.id}}
        serializer = SeatMapSerializer(self.seat1, context=context)
        self.assertEqual(serializer.data["status"], "reserved")

    def test_status_priority_purchased_over_reserved(self):
        context = {"ticket_seat_ids": {self.seat1.id}, "locked_seat_ids": {self.seat1.id}}
        serializer = SeatMapSerializer(self.seat1, context=context)
        self.assertEqual(serializer.data["status"], "purchased")


class ReserveSeatSerializerTest(TestCase):
    def test_valid_data(self):
        serializer = ReserveSeatSerializer(data={"seat_id": 1})
        self.assertTrue(serializer.is_valid())

    def test_missing_seat_id(self):
        serializer = ReserveSeatSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("seat_id", serializer.errors)


class CheckoutSerializerTest(TestCase):
    def test_valid_data(self):
        serializer = CheckoutSerializer(data={"seat_id": 1})
        self.assertTrue(serializer.is_valid())

    def test_missing_seat_id(self):
        serializer = CheckoutSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("seat_id", serializer.errors)


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test",
            duration=120,
            rating="PG",
            is_available=True,
        )
        self.room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)
        self.seat = Seat.objects.create(room=self.room, row="B", number=5)
        start_time = timezone.now() + timedelta(days=1)
        self.session = Session.objects.create(
            movie=self.movie, room=self.room, start_time=start_time, is_available=True
        )
        self.ticket = Ticket.objects.create(
            user=self.user, session=self.session, seat=self.seat, code=uuid.uuid4()
        )

    def test_contains_expected_fields(self):
        serializer = TicketSerializer(self.ticket)
        data = serializer.data
        self.assertEqual(
            set(data.keys()), {"id", "code", "movie", "start_time", "room", "seat"}
        )

    def test_seat_formatted(self):
        serializer = TicketSerializer(self.ticket)
        self.assertEqual(serializer.data["seat"], "FB-A5")

    def test_movie_from_related(self):
        serializer = TicketSerializer(self.ticket)
        self.assertEqual(serializer.data["movie"], "Test Movie")


class SessionsListViewTest(APITestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test",
            duration=120,
            rating="PG",
            is_available=True,
        )
        self.room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)
        start_time = timezone.now() + timedelta(days=1)
        self.session1 = Session.objects.create(
            movie=self.movie, room=self.room, start_time=start_time, is_available=True
        )
        start_time2 = timezone.now() + timedelta(days=2)
        self.session2 = Session.objects.create(
            movie=self.movie, room=self.room, start_time=start_time2, is_available=True
        )
        start_time3 = timezone.now() + timedelta(days=3)
        self.session3 = Session.objects.create(
            movie=self.movie, room=self.room, start_time=start_time3, is_available=False
        )

    def test_list_sessions_by_movie(self):
        url = reverse("sessions:sessions_list", kwargs={"movie_id": self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sessions = response.data["results"]
        self.assertEqual(len(sessions), 2)

    def test_list_only_available_sessions(self):
        url = reverse("sessions:sessions_list", kwargs={"movie_id": self.movie.id})
        response = self.client.get(url)
        sessions = response.data["results"]
        for session in sessions:
            self.assertTrue(session["movie_name"], "Test Movie")

    def test_sessions_ordered_by_start_time(self):
        url = reverse("sessions:sessions_list", kwargs={"movie_id": self.movie.id})
        response = self.client.get(url)
        sessions = response.data["results"]
        self.assertEqual(len(sessions), 2)

    def test_sessions_contains_expected_fields(self):
        url = reverse("sessions:sessions_list", kwargs={"movie_id": self.movie.id})
        response = self.client.get(url)
        session = response.data["results"][0]
        self.assertIn("id", session)
        self.assertIn("movie_name", session)
        self.assertIn("room_name", session)
        self.assertIn("start_time", session)

    def test_list_sessions_nonexistent_movie(self):
        url = reverse("sessions:sessions_list", kwargs={"movie_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
