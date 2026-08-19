# BÀI LÀM - API UPLOAD TÀI LIỆU HỌC TẬP

## PHẦN 1. PHÁT HIỆN LỖI

### 1. Lấy phần mở rộng file sai

Code cũ:

```python
extension = document.filename.split(".")[1]
```

Có hai vấn đề:

- Với `baitap.pdf.exe`, code lấy `pdf` thay vì phần mở rộng cuối cùng là `.exe`, nên file thực thi có thể bị chấp nhận.
- Với `README`, không có dấu `.`, câu lệnh có thể gây `IndexError`.

Cách sửa:

```python
extension = Path(document.filename or "").suffix.lower()
```

`Path.suffix` lấy phần mở rộng cuối cùng và `.lower()` giúp chuẩn hóa thành chữ thường.

---

### 2. Không tạo thư mục lưu trữ

Code khai báo:

```python
UPLOAD_FOLDER = "storage/documents"
```

nhưng không tạo thư mục.

Khi thư mục chưa tồn tại, `open(..., "wb")` có thể gây `FileNotFoundError`.

Cách sửa:

```python
UPLOAD_FOLDER = Path("storage/documents")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
```

`parents=True` tạo cả các thư mục cha cần thiết.

---

### 3. Không kiểm tra file rỗng

Code cũ đọc file rồi lưu ngay:

```python
content = await document.read()

with open(file_path, "wb") as output_file:
    output_file.write(content)
```

Không có điều kiện kiểm tra `len(content) == 0`.

Cách sửa:

```python
if len(content) == 0:
    raise HTTPException(status_code=400, detail="File must not be empty")
```

---

### 4. Không kiểm tra kích thước file

Code cũ cho phép lưu file có kích thước bất kỳ.

Quy tắc yêu cầu file tối đa 10 MB.

Cách sửa:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024

if len(content) > MAX_FILE_SIZE:
    raise HTTPException(
        status_code=413,
        detail="File must not exceed 10 MB"
    )
```

---

### 5. Không chuẩn hóa mã môn học

Code cũ lưu trực tiếp:

```python
course_code: str = Form(...)
```

Do đó `it215`, `IT215`, `It215` có thể được lưu khác nhau.

Cách sửa:

```python
course_code = course_code.strip().upper()
```

Ví dụ:

```text
it215 -> IT215
 It215  -> IT215
```

---

### 6. Không kiểm tra loại tài liệu

Code cũ không kiểm tra `document_type`.

Người dùng có thể gửi:

```text
video
image
exe
```

trong khi chỉ cho phép:

```text
lecture
assignment
reference
```

Cách sửa:

```python
ALLOWED_DOCUMENT_TYPES = {
    "lecture",
    "assignment",
    "reference",
}

document_type = document_type.strip().lower()

if document_type not in ALLOWED_DOCUMENT_TYPES:
    raise HTTPException(status_code=400, detail="Document type is not allowed")
```

---

### 7. Có nguy cơ ghi đè file

Code cũ:

```python
file_path = os.path.join(
    UPLOAD_FOLDER,
    document.filename,
)
```

Nếu hai người cùng upload:

```text
baitap.pdf
```

file thứ hai có thể ghi đè file thứ nhất.

Cách sửa:

```python
stored_filename = f"{uuid4().hex}{extension}"
```

Mỗi lần upload sẽ có một tên lưu trữ mới.

---

### 8. Không nên sử dụng trực tiếp tên file người dùng

Tên file do client gửi lên không nên được dùng trực tiếp làm tên file trên server.

Code cũ:

```python
document.filename
```

được dùng làm đường dẫn lưu trữ.

Code mới chỉ lấy tên gốc để trả về thông tin:

```python
original_filename = Path(document.filename or "").name
```

Sau đó tạo tên server riêng:

```python
stored_filename = f"{uuid4().hex}{extension}"
```

Như vậy tên file gốc được lưu lại nhưng không được sử dụng làm tên file vật lý trên server.

---

# TEST CASE

## Test case 1 - File có nhiều dấu chấm

**Input:**

```text
baitap.pdf.exe
```

**Kết quả hiện tại:** Có thể được chấp nhận vì code lấy phần tử `[1]` là `pdf`.

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** `split(".")[1]` không lấy phần mở rộng cuối cùng.

**Cách sửa:** Dùng `Path.suffix.lower()`.

---

## Test case 2 - File không có phần mở rộng

**Input:**

```text
README
```

**Kết quả hiện tại:** Có thể phát sinh `IndexError`.

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** `split(".")[1]` không tồn tại khi filename không có dấu chấm.

**Cách sửa:** Dùng `Path(filename).suffix` và kiểm tra extension rỗng.

---

## Test case 3 - File rỗng

**Input:**

```text
Filename: baitap.pdf
Size: 0 byte
```

**Kết quả hiện tại:** `200 OK`, file rỗng được lưu.

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** Không kiểm tra `len(content) == 0`.

---

## Test case 4 - Thư mục chưa tồn tại

**Input:**

```text
storage/documents không tồn tại
```

**Kết quả hiện tại:** API có thể crash với `FileNotFoundError`.

**Kết quả mong đợi:** API tự tạo:

```text
storage/
└── documents/
```

và upload thành công nếu các dữ liệu khác hợp lệ.

**Nguyên nhân:** Code cũ chỉ khai báo đường dẫn nhưng không tạo thư mục.

---

## Test case 5 - Mã môn học viết thường

**Input:**

```text
course_code = "it215"
```

**Kết quả hiện tại:** Có thể lưu thành `it215`.

**Kết quả mong đợi:**

```text
IT215
```

**Nguyên nhân:** Không chuẩn hóa bằng `upper()`.

---

## Test case 6 - Loại tài liệu không hợp lệ

**Input:**

```text
document_type = "video"
```

**Kết quả hiện tại:** Có thể được chấp nhận.

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** Code cũ không kiểm tra danh sách loại tài liệu.

---

## Test case 7 - File lớn hơn 10 MB

**Input:**

```text
Filename = large.pdf
Size > 10 MB
```

**Kết quả hiện tại:** Có thể được lưu.

**Kết quả mong đợi:** `413 Payload Too Large`

**Nguyên nhân:** Code cũ không kiểm tra kích thước file.

---

# PHẦN 2. SOURCE CODE ĐÃ SỬA

Source code trong `main.py` đã đáp ứng các yêu cầu:

- Dùng `Path.suffix`.
- Chuyển extension thành chữ thường bằng `.lower()`.
- Chuẩn hóa mã môn học bằng `.strip().upper()`.
- Kiểm tra `document_type`.
- Tạo thư mục bằng `mkdir(parents=True, exist_ok=True)`.
- Chặn file 0 byte.
- Chặn file trên 10 MB.
- Sinh tên file bằng UUID.
- Lưu cả tên file gốc và tên file trên server.
- Trả về đường dẫn file đã lưu.
- Không sử dụng trực tiếp tên file người dùng để lưu.
- Xử lý filename bất thường mà không gây `IndexError`.
- Trả về `400 Bad Request` cho dữ liệu/file không hợp lệ.
- Trả về `413 Payload Too Large` khi file vượt 10 MB.

## Chạy chương trình

Cài thư viện:

```bash
pip install -r requirements.txt
```

Chạy FastAPI:

```bash
uvicorn main:app --reload
```

Mở Swagger:

```text
http://127.0.0.1:8000/docs
```

Chạy test:

```bash
pytest -q
```
