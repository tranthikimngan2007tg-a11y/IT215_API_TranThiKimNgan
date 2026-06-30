import pytest
from fastapi.testclient import TestClient

def test_health_check_redirect(client: TestClient):
    # Kiểm tra điều hướng trang chủ mặc định sang Swagger Docs (không wrap do là redirect)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"

def test_auth_workflow(client: TestClient):
    # 1. Đăng ký tài khoản Giảng viên
    lecturer_data = {
        "username": "lecturer_john",
        "email": "john@school.edu",
        "password": "securepassword",
        "role": "lecturer"
    }
    response = client.post("/api/v1/auth/register/lecturer", json=lecturer_data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 201
    assert json_data["data"]["username"] == "lecturer_john"
    assert json_data["data"]["role"] == "lecturer"

    # 2. Đăng nhập tài khoản Giảng viên để lấy token
    login_data = {
        "username": "lecturer_john",
        "password": "securepassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 200
    token_json = json_data["data"]
    assert "access_token" in token_json
    assert token_json["role"] == "lecturer"
    lecturer_token = token_json["access_token"]
    lecturer_headers = {"Authorization": f"Bearer {lecturer_token}"}

    # 3. Đăng ký tài khoản và thông tin Sinh viên (Alice)
    student_data = {
        "username": "alice_smith",
        "email": "alice.smith@school.edu",
        "password": "password123",
        "student_code": "SV0001",
        "first_name": "Alice",
        "last_name": "Smith",
        "date_of_birth": "2003-04-12",
        "gender": "Female",
        "phone": "0911223344"
    }
    response = client.post("/api/v1/auth/register/student", json=student_data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 201
    assert json_data["data"]["student_code"] == "SV0001"
    
    # 4. Đăng nhập Sinh viên Alice để lấy token riêng
    student_login = {
        "username": "alice_smith",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=student_login)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 200
    student_token = json_data["data"]["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 5. Tạo lớp học dưới tư cách Giảng viên (Thao tác hợp lệ - Thành công)
    class_data = {
        "class_code": "PY101",
        "name": "Introduction to Python",
        "description": "Introductory Python programming class"
    }
    response = client.post("/api/v1/classes/", json=class_data, headers=lecturer_headers)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["statusCode"] == 201
    class_id = json_data["data"]["id"]

    # 6. Tạo lớp học dưới tư cách Sinh viên (Thao tác không hợp lệ - Trả về 403 Forbidden)
    response = client.post("/api/v1/classes/", json=class_data, headers=student_headers)
    assert response.status_code == 403
    json_data = response.json()
    assert json_data["statusCode"] == 403
    assert json_data["data"] is None

    # 7. Giảng viên cập nhật liên kết lớp học cho sinh viên Alice
    # Trước tiên, Giảng viên tìm kiếm hồ sơ của sinh viên Alice
    response = client.get("/api/v1/students/search?search_query=Alice", headers=lecturer_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["meta"]["totalRecord"] == 1
    alice_profile_id = json_data["data"][0]["id"]

    # Giảng viên gán lớp PY101 cho Alice
    response = client.put(f"/api/v1/students/{alice_profile_id}", json={"class_id": class_id}, headers=lecturer_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["data"]["class_id"] == class_id

    # 8. Giảng viên nhập điểm số môn học cho sinh viên Alice
    # Nhập điểm thi giữa kỳ (Trọng số 0.3)
    score_data = {
        "student_id": alice_profile_id,
        "subject_name": "Python Basics",
        "score_value": 9.0,
        "weight": 0.3,
        "remarks": "Điểm kiểm tra giữa kỳ đạt kết quả tốt"
    }
    response = client.post("/api/v1/scores/", json=score_data, headers=lecturer_headers)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["statusCode"] == 201

    # Nhập điểm thi cuối kỳ (Trọng số 0.7)
    score_data_final = {
        "student_id": alice_profile_id,
        "subject_name": "Python Basics",
        "score_value": 9.5,
        "weight": 0.7,
        "remarks": "Đồ án thực hành cuối kỳ xuất sắc"
    }
    response = client.post("/api/v1/scores/", json=score_data_final, headers=lecturer_headers)
    assert response.status_code == 201

    # 9. Giảng viên yêu cầu tính điểm GPA tích lũy của sinh viên Alice (Thành công)
    response = client.get(f"/api/v1/scores/student/{alice_profile_id}/gpa", headers=lecturer_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["data"]["gpa"] == 9.35  # Tính toán: (9.0 * 0.3 + 9.5 * 0.7) = 2.7 + 6.65 = 9.35

    # 10. Sinh viên Alice tự yêu cầu xem điểm GPA tích lũy của chính mình (Thành công)
    response = client.get(f"/api/v1/scores/student/{alice_profile_id}/gpa", headers=student_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["data"]["gpa"] == 9.35

    # 11. Sinh viên cố tình tự thêm điểm số môn học (Thao tác không hợp lệ - Trả về lỗi 403)
    fail_score = {
        "student_id": alice_profile_id,
        "subject_name": "Python Basics",
        "score_value": 10.0,
        "weight": 1.0
    }
    response = client.post("/api/v1/scores/", json=fail_score, headers=student_headers)
    assert response.status_code == 403
    json_data = response.json()
    assert json_data["statusCode"] == 403

def test_validation_and_integrity_errors(client: TestClient):
    # 1. Kiểm tra lỗi Pydantic validation trả về mã 400 Bad Request kèm thông điệp tiếng Việt kết thúc bằng dấu chấm
    invalid_student_data = {
        "username": "",  # Trống
        "email": "invalid-email",  # Định dạng email sai
        "password": "123",  # Quá ngắn
        "student_code": "SV0001",
        "first_name": "Test",
        "last_name": "Student",
        "date_of_birth": "2029-12-31",  # Ngày sinh ở tương lai
        "gender": "InvalidGender",  # Sai enum
        "phone": "abc"  # Định dạng số điện thoại sai
    }
    response = client.post("/api/v1/auth/register/student", json=invalid_student_data)
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["statusCode"] == 400
    assert json_data["message"] != ""
    assert isinstance(json_data["error"], list)
    
    # Kiểm tra tất cả các lỗi được dịch và kết thúc bằng dấu chấm
    for error_msg in json_data["error"]:
        assert error_msg.endswith(".")
        assert any(keyword in error_msg.lower() for keyword in ["không được để trống", "tối thiểu", "định dạng", "quá khứ", "chấp nhận", "email"])

    # 2. Kiểm tra lỗi trùng lặp tên đăng nhập (IntegrityError hoặc BadRequest thủ công)
    lecturer_data = {
        "username": "duplicate_user",
        "email": "dup@school.edu",
        "password": "securepassword",
        "role": "lecturer"
    }
    response = client.post("/api/v1/auth/register/lecturer", json=lecturer_data)
    assert response.status_code == 200
    
    # Đăng ký lại cùng thông tin tên đăng nhập để kích hoạt lỗi trùng lặp
    response = client.post("/api/v1/auth/register/lecturer", json=lecturer_data)
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["message"] == "Tên đăng nhập đã tồn tại trong hệ thống."

    # 3. Kiểm tra đăng ký sinh viên với class_id không tồn tại (trả về 400 và không bị 500)
    student_invalid_class = {
        "username": "student_invalid_class",
        "email": "invalid_class@school.edu",
        "password": "password123",
        "student_code": "SV9999",
        "first_name": "Invalid",
        "last_name": "Class",
        "date_of_birth": "2003-04-12",
        "gender": "Male",
        "phone": "0911223344",
        "class_id": 99999  # ID không tồn tại
    }
    response = client.post("/api/v1/auth/register/student", json=student_invalid_class)
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["message"] == "Không tìm thấy lớp học."

    # 4. Đăng nhập Giảng viên mới tạo ở trên để thực hiện các thao tác yêu cầu xác thực
    login_data = {
        "username": "duplicate_user",
        "password": "securepassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    lecturer_token = response.json()["data"]["access_token"]
    lecturer_headers = {"Authorization": f"Bearer {lecturer_token}"}

    # 5. Thêm điểm số với ID sinh viên không tồn tại (trả về 400 và không bị 500)
    invalid_score_data = {
        "student_id": 99999,  # ID sinh viên không tồn tại
        "subject_name": "Maths",
        "score_value": 8.5,
        "weight": 1.0,
        "remarks": "Điểm kiểm tra"
    }
    response = client.post("/api/v1/scores/", json=invalid_score_data, headers=lecturer_headers)
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["message"] == "ID sinh viên không tồn tại trên hệ thống."

    # 6. Tạo hồ sơ sinh viên với ID tài khoản không tồn tại (trả về 400 và không bị 500)
    invalid_student_profile = {
        "user_id": 99999,  # ID tài khoản không tồn tại
        "student_code": "SV8888",
        "first_name": "No",
        "last_name": "User",
        "date_of_birth": "2003-04-12",
        "gender": "Male",
        "phone": "0911223344"
    }
    response = client.post("/api/v1/students/", json=invalid_student_profile, headers=lecturer_headers)
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["message"] == "ID tài khoản người dùng không tồn tại."


