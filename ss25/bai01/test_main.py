import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, UPLOAD_DIR

client = TestClient(app)


def test_full_name_only_spaces():
    response = client.post(
        "/students/register",
        data={
            "full_name": "   ",
            "email": "student@example.com",
            "phone": "0987654321",
            "course": "FastAPI",
        },
        files={"avatar": ("avatar.jpg", b"fake image", "image/jpeg")},
    )
    assert response.status_code == 400


def test_phone_contains_letters():
    response = client.post(
        "/students/register",
        data={
            "full_name": "Nguyen Van A",
            "email": "student@example.com",
            "phone": "09876abcde",
            "course": "FastAPI",
        },
        files={"avatar": ("avatar.jpg", b"fake image", "image/jpeg")},
    )
    assert response.status_code == 400


def test_pdf_avatar_rejected():
    response = client.post(
        "/students/register",
        data={
            "full_name": "Nguyen Van A",
            "email": "student@example.com",
            "phone": "0987654321",
            "course": "FastAPI",
        },
        files={"avatar": ("student-profile.pdf", b"%PDF", "application/pdf")},
    )
    assert response.status_code == 400


def test_avatar_over_2mb_rejected():
    large_file = b"x" * (2 * 1024 * 1024 + 1)

    response = client.post(
        "/students/register",
        data={
            "full_name": "Nguyen Van A",
            "email": "student@example.com",
            "phone": "0987654321",
            "course": "FastAPI",
        },
        files={"avatar": ("large.jpg", large_file, "image/jpeg")},
    )
    assert response.status_code == 413


def test_duplicate_original_filename_does_not_overwrite():
    data = {
        "full_name": "Nguyen Van A",
        "email": "student@example.com",
        "phone": "0987654321",
        "course": "FastAPI",
    }

    first = client.post(
        "/students/register",
        data=data,
        files={"avatar": ("avatar.jpg", b"first image", "image/jpeg")},
    )

    second = client.post(
        "/students/register",
        data={
            **data,
            "email": "student2@example.com",
            "phone": "0123456789",
        },
        files={"avatar": ("avatar.jpg", b"second image", "image/jpeg")},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    first_path = Path(first.json()["data"]["avatar"])
    second_path = Path(second.json()["data"]["avatar"])

    assert first_path.name != second_path.name
    assert first_path.read_bytes() == b"first image"
    assert second_path.read_bytes() == b"second image"
