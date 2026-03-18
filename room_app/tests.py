from django.db import IntegrityError
from django.test import TestCase

from room_app.models import Room, Seat


class RoomModelTest(TestCase):
    def test_create_room(self):
        room = Room.objects.create(name="Sala 1", total_rows=10, seats_per_row=20)
        self.assertEqual(str(room), "Sala 1")
        self.assertEqual(room.name, "Sala 1")
        self.assertEqual(room.total_rows, 10)
        self.assertEqual(room.seats_per_row, 20)

    def test_room_total_seats(self):
        room = Room.objects.create(name="Sala 2", total_rows=5, seats_per_row=10)
        total_seats = room.total_rows * room.seats_per_row
        self.assertEqual(total_seats, 50)

    def test_room_name_max_length(self):
        long_name = "x" * 101
        room = Room(name=long_name, total_rows=5, seats_per_row=10)
        with self.assertRaises(Exception):
            room.full_clean()


class SeatModelTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Sala 1", total_rows=5, seats_per_row=10)

    def test_create_seat(self):
        seat = Seat.objects.create(room=self.room, row="A", number=1)
        self.assertEqual(str(seat), "Sala 1 - A 1")
        self.assertEqual(seat.room, self.room)
        self.assertEqual(seat.row, "A")
        self.assertEqual(seat.number, 1)

    def test_seat_unique_constraint(self):
        Seat.objects.create(room=self.room, row="A", number=1)
        with self.assertRaises(IntegrityError):
            Seat.objects.create(room=self.room, row="A", number=1)

    def test_seat_same_row_different_number(self):
        seat1 = Seat.objects.create(room=self.room, row="A", number=1)
        seat2 = Seat.objects.create(room=self.room, row="A", number=2)
        self.assertNotEqual(seat1.id, seat2.id)

    def test_seat_different_row_same_number(self):
        seat1 = Seat.objects.create(room=self.room, row="A", number=1)
        seat2 = Seat.objects.create(room=self.room, row="B", number=1)
        self.assertNotEqual(seat1.id, seat2.id)

    def test_seat_cascade_delete_room(self):
        Seat.objects.create(room=self.room, row="A", number=1)
        Seat.objects.create(room=self.room, row="A", number=2)
        self.assertEqual(Seat.objects.count(), 2)
        self.room.delete()
        self.assertEqual(Seat.objects.count(), 0)

    def test_seat_same_position_different_rooms(self):
        room2 = Room.objects.create(name="Sala 2", total_rows=5, seats_per_row=10)
        seat1 = Seat.objects.create(room=self.room, row="A", number=1)
        seat2 = Seat.objects.create(room=room2, row="A", number=1)
        self.assertNotEqual(seat1.id, seat2.id)


class SeatManagerTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Sala 1", total_rows=3, seats_per_row=3)
        Seat.objects.create(room=self.room, row="A", number=1)
        Seat.objects.create(room=self.room, row="A", number=2)
        Seat.objects.create(room=self.room, row="B", number=1)

    def test_seats_by_row(self):
        a_seats = Seat.objects.filter(room=self.room, row="A")
        self.assertEqual(a_seats.count(), 2)

    def test_seats_by_room(self):
        seats = Seat.objects.filter(room=self.room)
        self.assertEqual(seats.count(), 3)

    def test_seat_ordering(self):
        seats = list(Seat.objects.filter(room=self.room).order_by("row", "number"))
        self.assertEqual(seats[0].row, "A")
        self.assertEqual(seats[0].number, 1)
        self.assertEqual(seats[1].row, "A")
        self.assertEqual(seats[1].number, 2)
        self.assertEqual(seats[2].row, "B")
        self.assertEqual(seats[2].number, 1)
