from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status

app = FastAPI()

UPLOAD_FOLDER = Path("storage/documents")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
ALLOWED_DOCUMENT_TYPES = {"lecture", "assignment", "reference"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.post("/documents")
async def upload_document(
    title: str = Form(...),
    course_code: str = Form(...),
    document_type: str = Form(...),
    description: str = Form(""),
    document: UploadFile = File(...),
):
    # 1. Validate and normalize text fields.
    title = title.strip()
    course_code = course_code.strip().upper()
    document_type = document_type.strip().lower()
    description = description.strip()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document title is required",
        )

    if not course_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code is required",
        )

    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document type is not allowed",
        )

    # 2. Safely get the extension from the filename.
    original_filename = Path(document.filename or "").name
    extension = Path(original_filename).suffix.lower()

    if not original_filename or not extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have an extension",
        )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type is not allowed",
        )

    # 3. Read the uploaded file and validate size.
    content = await document.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must not be empty",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File must not exceed 10 MB",
        )

    # 4. Generate a unique server-side filename.
    stored_filename = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_FOLDER / stored_filename

    # The server never uses the user's original filename as the storage name.
    with open(file_path, "wb") as output_file:
        output_file.write(content)

    return {
        "success": True,
        "message": "Document uploaded successfully",
        "data": {
            "title": title,
            "course_code": course_code,
            "document_type": document_type,
            "description": description,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_path": str(file_path),
        },
    }
