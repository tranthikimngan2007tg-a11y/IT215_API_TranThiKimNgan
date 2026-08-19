from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_COURSES = [
    "Python Basic",
    "FastAPI",
    "Data Analysis",
]

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


def validate_email(email: str) -> bool:
    email = email.strip()
    return "@" in email and not email.startswith("@") and not email.endswith("@")


def get_safe_filename(original_filename: str) -> str:
    extension = Path(original_filename or "").suffix.lower()
    return f"{uuid4().hex}{extension}"


@app.post("/students/register")
async def register_student(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    course: str = Form(...),
    avatar: UploadFile = File(...),
):
    # 1. Validate text fields BEFORE reading/saving the uploaded file.
    full_name = full_name.strip()
    email = email.strip()
    phone = phone.strip()
    course = course.strip()

    if not full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name is required",
        )

    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )

    if len(phone) != 10 or not phone.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must contain exactly 10 digits",
        )

    if course not in ALLOWED_COURSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is not available",
        )

    # 2. Validate extension and MIME type.
    original_name = avatar.filename or ""
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar must be JPG or PNG",
        )

    if avatar.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid avatar content type",
        )

    # 3. Read the file only after all form fields are valid.
    content = await avatar.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Avatar file must not exceed 2 MB",
        )

    # 4. Never use the user's original filename for storage.
    safe_filename = get_safe_filename(original_name)
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as file:
        file.write(content)

    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "course": course,
            "avatar": str(file_path),
        },
    }
