from django.test import TestCase
from .models import *
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.db = get_user_model()

    def test_create_user(self):
        u = self.db.objects.create_user(email="test@mail.com", username="testuser",
                                             password="securesercret!@12")
        self.assertEqual("testuser", u.username)
        self.assertEqual("test@mail.com", u.email)
        self.assertNotEqual("securesercret!@12", u.password)
        self.assertFalse(u.is_superuser)
        self.assertFalse(u.is_staff)
        self.assertFalse(u.is_active)
        self.assertIn(u.email, str(u))
        self.assertIn(u.username, str(u))

    # Checking for TypeError instead of ValueError because the django class checks for required fields
    # before the reaching the custom model method (create_user)
    def test_create_user_with_no_username(self):
        with self.assertRaises(TypeError):
            self.db.objects.create_user(email="test@mail.com", password="securesercret!@12")

    def test_create_user_with_no_email(self):
        with self.assertRaises(TypeError):
            self.db.objects.create_user(username="testuser", password="securesercret!@12")

    def test_create_user_with_no_password(self):
        with self.assertRaises(TypeError):
            self.db.objects.create_user(email="test@mail.com", username="testuser")

    def test_create_superuser(self):
        u = self.db.objects.create_superuser(email="test@mail.com", username="testsuperuser",
                                             password="securesercret!@12")
        self.assertEqual("testsuperuser", u.username)
        self.assertEqual("test@mail.com", u.email)
        self.assertNotEqual("securesercret!@12", u.password)
        self.assertTrue(u.is_superuser)
        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_active)
        self.assertIn(u.email, str(u))
        self.assertIn(u.username, str(u))

    def test_create_superuser_is_not_staff(self):
        with self.assertRaises(ValueError):
            self.db.objects.create_superuser(email="test@mail.com", username="testsuperuser",
                                             password="securesercret!@12", is_staff=False)

    def test_create_superuser_is_not_superuser(self):
        with self.assertRaises(ValueError):
            self.db.objects.create_superuser(email="test@mail.com", username="testsuperuser",
                                             password="securesercret!@12", is_superuser=False)

    def test_create_superuser_is_not_active(self):
        with self.assertRaises(ValueError):
            self.db.objects.create_superuser(email="test@mail.com", username="testsuperuser",
                                             password="securesercret!@12", is_active=False)
