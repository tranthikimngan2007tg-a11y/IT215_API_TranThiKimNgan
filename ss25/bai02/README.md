# Document Upload API - FastAPI

## Cấu trúc thư mục

```text
document_upload_assignment/
├── main.py
├── test_main.py
├── BAI_LAM.md
├── README.md
├── requirements.txt
└── storage/
    └── documents/
```

## Chức năng

API `/documents` nhận:

- `title`
- `course_code`
- `document_type`
- `description`
- `document`

Loại tài liệu:

- `lecture`
- `assignment`
- `reference`

Định dạng file:

- `.pdf`
- `.doc`
- `.docx`
- `.ppt`
- `.pptx`

Giới hạn:

- Không được rỗng.
- Không quá 10 MB.
- Tên lưu trên server được sinh bằng UUID.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy

```bash
uvicorn main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Test

```bash
pytest -q
```
