from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def valid_data():
    return {
        "title": "Bai giang FastAPI",
        "course_code": "it215",
        "document_type": "lecture",
        "description": "Tai lieu hoc tap",
    }


def test_multiple_dots_filename_rejected():
    response = client.post(
        "/documents",
        data=valid_data(),
        files={"document": ("baitap.pdf.exe", b"data", "application/octet-stream")},
    )

    assert response.status_code == 400


def test_filename_without_extension_rejected():
    response = client.post(
        "/documents",
        data=valid_data(),
        files={"document": ("README", b"data", "text/plain")},
    )

    assert response.status_code == 400


def test_empty_file_rejected():
    response = client.post(
        "/documents",
        data=valid_data(),
        files={"document": ("baitap.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 400


def test_course_code_is_normalized_to_uppercase():
    response = client.post(
        "/documents",
        data={
            **valid_data(),
            "course_code": "it215",
        },
        files={"document": ("baitap.pdf", b"PDF test data", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["data"]["course_code"] == "IT215"


def test_duplicate_original_filename_creates_unique_server_files():
    first = client.post(
        "/documents",
        data=valid_data(),
        files={"document": ("baitap.pdf", b"first file", "application/pdf")},
    )

    second = client.post(
        "/documents",
        data={
            **valid_data(),
            "course_code": "IT216",
        },
        files={"document": ("baitap.pdf", b"second file", "application/pdf")},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    first_data = first.json()["data"]
    second_data = second.json()["data"]

    assert first_data["original_filename"] == "baitap.pdf"
    assert second_data["original_filename"] == "baitap.pdf"
    assert first_data["stored_filename"] != second_data["stored_filename"]

    assert Path(first_data["file_path"]).read_bytes() == b"first file"
    assert Path(second_data["file_path"]).read_bytes() == b"second file"


def test_document_type_is_required_from_allowed_list():
    response = client.post(
        "/documents",
        data={
            **valid_data(),
            "document_type": "video",
        },
        files={"document": ("baitap.pdf", b"data", "application/pdf")},
    )

    assert response.status_code == 400


def test_file_over_10mb_rejected():
    large_content = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/documents",
        data=valid_data(),
        files={"document": ("large.pdf", large_content, "application/pdf")},
    )

    assert response.status_code == 413
