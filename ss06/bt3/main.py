from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

app = FastAPI()


class RoomStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"


class CreateRoom(BaseModel):
    code: str
    name: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    status: RoomStatus


rooms = [
    {"id": 1, "code": "R101", "name": "Room 101", "capacity": 30, "status": "AVAILABLE"},
    {"id": 2, "code": "R102", "name": "Room 102", "capacity": 20, "status": "AVAILABLE"},
    {"id": 3, "code": "R103", "name": "Room 103", "capacity": 40, "status": "MAINTENANCE"}
]

room_bookings = [
    {
        "id": 1,
        "room_id": 1,
        "class_name": "Python Basic",
        "student_count": 25,
        "date": "2026-07-01",
        "slot": "MORNING"
    }
]


@app.get("/rooms")
def get_rooms(
    keyword: Optional[str] = None,
    status: Optional[RoomStatus] = None,
    min_capacity: Optional[int] = None
):
    result = rooms

    if keyword:
        keyword = keyword.lower()
        result = [
            room for room in result
            if keyword in room["code"].lower()
            or keyword in room["name"].lower()
        ]

    if status is not None:
        result = [
            room for room in result
            if room["status"] == status.value
        ]

    if min_capacity is not None:
        result = [
            room for room in result
            if room["capacity"] >= min_capacity
        ]

    return result


@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    for room in rooms:
        if room["id"] == room_id:
            return room

    raise HTTPException(
        status_code=404,
        detail="Room not found"
    )


@app.post("/rooms")
def create_room(room: CreateRoom):

    for r in rooms:
        if r["code"] == room.code:
            raise HTTPException(
                status_code=409,
                detail="Room code already exists"
            )

    max_id = 0

    for r in rooms:
        if r["id"] > max_id:
            max_id = r["id"]

    new_room = {
        "id": max_id + 1,
        "code": room.code,
        "name": room.name,
        "capacity": room.capacity,
        "status": room.status.value
    }

    rooms.append(new_room)

    return new_room


@app.put("/rooms/{room_id}")
def update_room(room_id: int, room: CreateRoom):

    for r in rooms:
        if r["code"] == room.code and r["id"] != room_id:
            raise HTTPException(
                status_code=409,
                detail="Room code already exists"
            )

    for r in rooms:
        if r["id"] == room_id:
            r["code"] = room.code
            r["name"] = room.name
            r["capacity"] = room.capacity
            r["status"] = room.status.value
            return r

    raise HTTPException(
        status_code=404,
        detail="Room not found"
    )


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):

    for room in rooms:
        if room["id"] == room_id:
            rooms.remove(room)
            return {
                "message": "Delete successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Room not found"
    )
class BookingSlot(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"


class CreateRoomBooking(BaseModel):
    room_id: int
    class_name: str = Field(min_length=1)
    student_count: int = Field(gt=0)
    date: str
    slot: BookingSlot


@app.get("/room-bookings")
def get_room_bookings():
    return room_bookings


@app.post("/room-bookings")
def create_room_booking(booking: CreateRoomBooking):

    room = None

    for r in rooms:
        if r["id"] == booking.room_id:
            room = r
            break

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    if room["status"] != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="Room is not available"
        )

    if booking.student_count > room["capacity"]:
        raise HTTPException(
            status_code=400,
            detail="Student count exceeds room capacity"
        )

    for b in room_bookings:
        if (
            b["room_id"] == booking.room_id
            and b["date"] == booking.date
            and b["slot"] == booking.slot.value
        ):
            raise HTTPException(
                status_code=409,
                detail="Room already booked"
            )

    max_id = 0

    for b in room_bookings:
        if b["id"] > max_id:
            max_id = b["id"]

    new_booking = {
        "id": max_id + 1,
        "room_id": booking.room_id,
        "class_name": booking.class_name,
        "student_count": booking.student_count,
        "date": booking.date,
        "slot": booking.slot.value
    }

    room_bookings.append(new_booking)

    return new_booking