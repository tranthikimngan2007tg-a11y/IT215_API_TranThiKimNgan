# BÀI LÀM - KIỂM TRA VÀ SỬA API ĐĂNG KÝ HỒ SƠ SINH VIÊN

## PHẦN 1. PHÁT HIỆN LỖI

### Lỗi 1 - Kiểm tra họ tên

Code cũ:

```python
if full_name == "":
```

Sai vì `"   "` không bằng chuỗi rỗng. Người dùng vẫn có thể gửi họ tên chỉ gồm khoảng trắng.

Cách sửa:

```python
full_name = full_name.strip()

if not full_name:
    raise HTTPException(status_code=400, detail="Full name is required")
```

### Lỗi 2 - Kiểm tra số điện thoại

Code cũ:

```python
if len(phone) < 10:
```

Sai vì chỉ kiểm tra độ dài tối thiểu. Chuỗi `09876abcde` có đúng 10 ký tự nhưng chứa chữ.

Cách sửa:

```python
if len(phone) != 10 or not phone.isdigit():
```

Điều kiện này yêu cầu đúng 10 ký tự và tất cả đều là chữ số.

### Lỗi 3 - Email chưa được kiểm tra

Code cũ không kiểm tra email.

Cách sửa:

```python
email = email.strip()

if "@" not in email or email.startswith("@") or email.endswith("@"):
    raise HTTPException(status_code=400, detail="Invalid email")
```

Đây là kiểm tra email cơ bản theo yêu cầu bài tập.

### Lỗi 4 - Chưa kiểm tra định dạng ảnh

Code cũ lấy trực tiếp:

```python
file_path = UPLOAD_DIR / avatar.filename
```

Như vậy PDF hoặc các file khác cũng có thể được lưu.

Cách sửa là kiểm tra phần mở rộng và MIME type:

```python
extension = Path(avatar.filename or "").suffix.lower()

if extension not in {".jpg", ".jpeg", ".png"}:
    raise HTTPException(status_code=400, detail="Avatar must be JPG or PNG")
```

### Lỗi 5 - Chưa giới hạn kích thước file

Code cũ đọc toàn bộ file:

```python
content = await avatar.read()
```

sau đó lưu ngay, không kiểm tra kích thước.

Cách sửa:

```python
content = await avatar.read()

if len(content) > 2 * 1024 * 1024:
    raise HTTPException(
        status_code=413,
        detail="Avatar file must not exceed 2 MB"
    )
```

### Lỗi 6 - Có nguy cơ ghi đè file

Code cũ:

```python
file_path = UPLOAD_DIR / avatar.filename
```

Nếu hai sinh viên cùng upload `avatar.jpg`, file sau sẽ ghi đè file trước.

Ngoài ra, dùng trực tiếp tên file do người dùng gửi lên là không an toàn.

Cách sửa:

```python
safe_filename = f"{uuid4().hex}{extension}"
file_path = UPLOAD_DIR / safe_filename
```

Tên lưu trữ được sinh mới cho mỗi file.

### Lỗi 7 - Có thể lưu file trước khi xác thực đầy đủ

File phải chỉ được lưu sau khi tất cả dữ liệu đã hợp lệ.

Trong source mới, các trường họ tên, email, số điện thoại, khóa học và định dạng file được kiểm tra trước; chỉ sau đó file mới được đọc và lưu.

---

# TEST CASE

## Test case 1 - Họ tên chỉ chứa khoảng trắng

**Dữ liệu đầu vào:**

```text
full_name = "   "
email = "student@example.com"
phone = "0987654321"
course = "FastAPI"
avatar = avatar.jpg
```

**Kết quả hiện tại:** `200 OK`

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** Code cũ chỉ kiểm tra `full_name == ""`, không loại bỏ khoảng trắng bằng `strip()`.

---

## Test case 2 - Số điện thoại chứa chữ

**Dữ liệu đầu vào:**

```text
full_name = "Nguyen Van A"
email = "student@example.com"
phone = "09876abcde"
course = "FastAPI"
avatar = avatar.jpg
```

**Kết quả hiện tại:** `200 OK`

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** Code cũ chỉ kiểm tra `len(phone) < 10`. Chuỗi có chữ vẫn có thể có độ dài từ 10 trở lên.

---

## Test case 3 - Upload PDF

**Dữ liệu đầu vào:**

```text
full_name = "Nguyen Van A"
email = "student@example.com"
phone = "0987654321"
course = "FastAPI"
avatar = student-profile.pdf
```

**Kết quả hiện tại:** `200 OK`

**Kết quả mong đợi:** `400 Bad Request`

**Nguyên nhân:** Code cũ không kiểm tra phần mở rộng hoặc MIME type của file.

---

## Test case 4 - Upload ảnh lớn hơn 2 MB

**Dữ liệu đầu vào:**

```text
full_name = "Nguyen Van A"
email = "student@example.com"
phone = "0987654321"
course = "FastAPI"
avatar = large.jpg
size > 2 MB
```

**Kết quả hiện tại:** `200 OK`

**Kết quả mong đợi:** `413 Payload Too Large`

**Nguyên nhân:** Code cũ không kiểm tra kích thước file trước khi lưu.

---

## Test case 5 - Hai sinh viên upload cùng tên file

**Dữ liệu đầu vào:**

```text
Sinh viên 1: avatar.jpg
Sinh viên 2: avatar.jpg
```

**Kết quả hiện tại:** File của sinh viên 2 ghi đè file của sinh viên 1.

**Kết quả mong đợi:** Hai file có tên lưu trữ khác nhau và đều được giữ lại.

**Nguyên nhân:** Code cũ sử dụng trực tiếp `avatar.filename` làm tên file lưu trữ.

---

# PHẦN 2. SOURCE CODE ĐÃ SỬA

Các yêu cầu đã được đáp ứng:

- Dùng `strip()` để kiểm tra chuỗi rỗng.
- Kiểm tra email cơ bản có ký tự `@`.
- Số điện thoại phải đúng 10 chữ số.
- Chỉ nhận JPG/JPEG và PNG.
- File không vượt quá 2 MB.
- Sinh tên file bằng UUID để tránh trùng.
- Không dùng trực tiếp tên file người dùng gửi để lưu.
- Dùng mã HTTP `400` cho dữ liệu không hợp lệ.
- Dùng mã HTTP `413` khi file vượt quá 2 MB.
- Chỉ lưu file sau khi các trường dữ liệu và file đã được kiểm tra hợp lệ.

## Lưu ý

`multipart/form-data` cho phép gửi đồng thời các trường `Form` và file `UploadFile`.

Trong bài này, việc kiểm tra kích thước được thực hiện sau khi đọc file vào bộ nhớ để đơn giản và phù hợp với bài thực hành. Với hệ thống production, nên giới hạn request/file ngay từ tầng server hoặc đọc theo từng chunk để tránh tiêu tốn bộ nhớ khi người dùng gửi file cực lớn.
