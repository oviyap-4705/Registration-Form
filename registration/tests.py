import shutil
import tempfile
from secrets import token_urlsafe

from django.contrib.auth.hashers import check_password, make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Registration


# Uploaded files created during tests go to a temporary folder,
# which is deleted when the test module finishes.
TEMP_MEDIA_ROOT = tempfile.mkdtemp()
media_settings = override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)

# A random value for every test run, so no password is hard-coded.
TEST_PASSWORD = token_urlsafe(12)

INVALID_LOGIN_MESSAGE = "Invalid email or password."
FAKE_IMAGE_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 16


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


def create_registration(**overrides):
    """Create a Registration directly in the database, with a hashed password."""
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": make_password(TEST_PASSWORD),
        "phone_number": "9876543210",
        "address": "12 Sample Street",
        "dob": "2000-01-01",
        "website": "https://example.com",
        "state": "Tamil Nadu",
        "languages": "Tamil, English",
        "gender": "Female",
        "skills": "Python, Django",
        "experience": 2,
        "photo": SimpleUploadedFile(
            "photo.png", FAKE_IMAGE_BYTES, content_type="image/png"
        ),
        "resume": SimpleUploadedFile(
            "resume.pdf", b"%PDF-1.4 test", content_type="application/pdf"
        ),
        "audio": SimpleUploadedFile(
            "audio.mp3", b"audio", content_type="audio/mpeg"
        ),
        "video": SimpleUploadedFile(
            "video.mp4", b"video", content_type="video/mp4"
        ),
    }
    data.update(overrides)

    return Registration.objects.create(**data)


def api_payload(**overrides):
    """Form data for the API (no files, they are optional)."""
    payload = {
        "name": "API User",
        "email": "api@example.com",
        "password": TEST_PASSWORD,
        "phone_number": "9123456780",
        "address": "5 Sample Road",
        "dob": "1999-05-20",
        "website": "https://api.example.com",
        "state": "Tamil Nadu",
        "languages": "Tamil, English",
        "gender": "Female",
        "skills": "Python",
        "experience": 1,
    }
    payload.update(overrides)

    return payload


def log_in(client, registration):
    """Simulate a logged-in user by setting the session value the views use."""
    session = client.session
    session["registration_id"] = registration.id
    session.save()


class PageTests(TestCase):

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_unsupported_methods_are_rejected(self):
        self.assertEqual(self.client.post(reverse("home")).status_code, 405)
        self.assertEqual(self.client.post(reverse("register")).status_code, 405)


@media_settings
class LoginTests(TestCase):

    def setUp(self):
        self.registration = create_registration()

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_unknown_email_shows_error(self):
        response = self.client.post(
            reverse("login"),
            {"email": "nobody@example.com", "password": TEST_PASSWORD},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error"], INVALID_LOGIN_MESSAGE)

    def test_wrong_password_shows_error(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.registration.email, "password": "wrong-value"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error"], INVALID_LOGIN_MESSAGE)
        self.assertNotIn("registration_id", self.client.session)

    def test_successful_login_redirects_to_profile(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.registration.email, "password": TEST_PASSWORD},
        )

        self.assertRedirects(
            response, "/profile/", fetch_redirect_response=False
        )
        self.assertEqual(
            self.client.session["registration_id"], self.registration.id
        )


@media_settings
class ProfileTests(TestCase):

    def setUp(self):
        self.registration = create_registration()

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(reverse("profile"))

        self.assertRedirects(
            response, "/login/", fetch_redirect_response=False
        )

    def test_stale_session_is_cleared(self):
        session = self.client.session
        session["registration_id"] = 999999
        session.save()

        response = self.client.get(reverse("profile"))

        self.assertRedirects(
            response, "/login/", fetch_redirect_response=False
        )
        self.assertNotIn("registration_id", self.client.session)

    def test_profile_page_shows_registration(self):
        log_in(self.client, self.registration)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["registration"], self.registration)

    def test_update_details_keeps_password_when_left_blank(self):
        log_in(self.client, self.registration)

        response = self.client.post(
            reverse("profile"),
            {"name": "Updated Name", "password": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["success"], "Details updated successfully."
        )

        self.registration.refresh_from_db()
        self.assertEqual(self.registration.name, "Updated Name")
        self.assertTrue(
            check_password(TEST_PASSWORD, self.registration.password)
        )

    def test_update_password_stores_a_hash(self):
        log_in(self.client, self.registration)
        new_value = token_urlsafe(12)

        response = self.client.post(
            reverse("profile"),
            {"password": new_value},
        )

        self.assertEqual(response.status_code, 200)

        self.registration.refresh_from_db()
        self.assertNotEqual(self.registration.password, new_value)
        self.assertTrue(check_password(new_value, self.registration.password))

    def test_invalid_update_shows_errors(self):
        log_in(self.client, self.registration)

        response = self.client.post(
            reverse("profile"),
            {"email": "not-an-email"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["errors"])

        self.registration.refresh_from_db()
        self.assertEqual(self.registration.email, "test@example.com")


@media_settings
class LogoutTests(TestCase):

    def setUp(self):
        self.registration = create_registration()

    def test_logout_clears_session_and_redirects_home(self):
        log_in(self.client, self.registration)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.assertNotIn("registration_id", self.client.session)

    def test_logout_also_accepts_post(self):
        log_in(self.client, self.registration)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, "/", fetch_redirect_response=False)


@media_settings
class RegistrationApiTests(APITestCase):

    def test_list_returns_registrations_without_passwords(self):
        create_registration()

        response = self.client.get(reverse("registrations"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertNotIn("password", response.data[0])

    def test_create_registration_stores_hashed_password(self):
        response = self.client.post(
            reverse("registrations"), api_payload(), format="multipart"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Registration successful")
        self.assertNotIn("password", response.data["data"])

        stored = Registration.objects.get(email="api@example.com")
        self.assertNotEqual(stored.password, TEST_PASSWORD)
        self.assertTrue(check_password(TEST_PASSWORD, stored.password))

    def test_create_with_missing_fields_fails(self):
        response = self.client.post(
            reverse("registrations"),
            {"name": "Only A Name"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Registration.objects.count(), 0)


@media_settings
class RegistrationDetailApiTests(APITestCase):

    def setUp(self):
        self.registration = create_registration()
        self.url = reverse(
            "registration_detail", args=[self.registration.id]
        )

    def test_get_one_registration(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test User")

    def test_get_missing_registration_returns_404(self):
        response = self.client.get(
            reverse("registration_detail", args=[999999])
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "Registration not found")

    def test_patch_updates_fields(self):
        response = self.client.patch(
            self.url, {"name": "Patched Name"}, format="multipart"
        )

        self.assertEqual(response.status_code, 200)

        self.registration.refresh_from_db()
        self.assertEqual(self.registration.name, "Patched Name")

    def test_patch_password_is_hashed(self):
        new_value = token_urlsafe(12)

        response = self.client.patch(
            self.url, {"password": new_value}, format="multipart"
        )

        self.assertEqual(response.status_code, 200)

        self.registration.refresh_from_db()
        self.assertNotEqual(self.registration.password, new_value)
        self.assertTrue(check_password(new_value, self.registration.password))

    def test_patch_with_invalid_data_fails(self):
        response = self.client.patch(
            self.url, {"email": "not-an-email"}, format="multipart"
        )

        self.assertEqual(response.status_code, 400)

    def test_delete_removes_registration(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Registration.objects.filter(id=self.registration.id).exists()
        )