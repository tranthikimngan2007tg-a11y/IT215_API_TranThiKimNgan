import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_student.db")

from fastapi.testclient import TestClient

from main import app
from app.database import Base, engine


class StudentAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_crud_flow(self):
        create_response = self.client.post(
            "/students",
            json={
                "full_name": "Nguyen Van A",
                "email": "a@example.com",
                "major": "Computer Science",
                "gpa": 3.5,
            },
        )
        self.assertEqual(create_response.status_code, 200)
        created_student = create_response.json()
        self.assertEqual(created_student["full_name"], "Nguyen Van A")
        self.assertTrue(created_student["id"] > 0)

        list_response = self.client.get("/students")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        detail_response = self.client.get(f"/students/{created_student['id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["email"], "a@example.com")

        update_response = self.client.put(
            f"/students/{created_student['id']}",
            json={"major": "Software Engineering", "gpa": 3.8},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["major"], "Software Engineering")

        delete_response = self.client.delete(f"/students/{created_student['id']}")
        self.assertEqual(delete_response.status_code, 200)

        after_delete = self.client.get("/students")
        self.assertEqual(after_delete.status_code, 200)
        self.assertEqual(after_delete.json(), [])


if __name__ == "__main__":
    unittest.main()
