# Bài tập: Đăng ký hồ sơ sinh viên - FastAPI

## Cấu trúc

- `main.py`: source code đã sửa.
- `test_main.py`: 5 test case kiểm thử.
- `BAI_LAM.md`: Phần 1 phát hiện lỗi + Phần 2 giải thích source code.
- `requirements.txt`: thư viện cần cài.
- `uploads/`: thư mục lưu ảnh sau khi đăng ký thành công.

## Cài đặt

```bash
python -m pip install -r requirements.txt
```

## Chạy API

```bash
uvicorn main:app --reload
```

Mở Swagger:

```text
http://127.0.0.1:8000/docs
```

## Chạy test

```bash
pytest -q
```
