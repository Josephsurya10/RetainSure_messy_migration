import unittest
from app import app

class UserApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_user(self):
        payload = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "strongpass"
        }
        response = self.app.post('/users', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("User created", response.get_json().get("message", ""))

    def test_duplicate_email(self):
        payload = {
            "name": "Test User2",
            "email": "testuser@example.com",
            "password": "strongpass"
        }
        response = self.app.post('/users', json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Email already exists", response.get_json().get("error", ""))

    def test_invalid_email(self):
        payload = {
            "name": "Bad Email",
            "email": "notanemail",
            "password": "123456"
        }
        response = self.app.post('/users', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email format", response.get_json().get("error", ""))

    def test_short_password(self):
        payload = {
            "name": "ShortPass",
            "email": "shortpass@example.com",
            "password": "123"
        }
        response = self.app.post('/users', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Password too short", response.get_json().get("error", ""))

    def test_login_success(self):
        payload = {
            "email": "testuser@example.com",
            "password": "strongpass"
        }
        response = self.app.post('/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get("status"), "success")

    def test_login_failure(self):
        payload = {
            "email": "testuser@example.com",
            "password": "wrongpass"
        }
        response = self.app.post('/login', json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json().get("status"), "failed")

    def test_get_nonexistent_user(self):
        response = self.app.get('/user/999999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_json().get("error", ""))

if __name__ == '__main__':
    unittest.main()
