from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User, PasswordResetOTPCode, PhoneResetOTP
from account.api.v1.tokens import PasswordResetToken


pytestmark = pytest.mark.django_db


# ==================================================
# Helpers
# ==================================================

def create_user(
    phone="09123456789",
    user_name="ali",
    password="Test12345!",
    is_active=True,
):
    return User.objects.create_user(
        phone=phone,
        password=password,
        first_name="Ali",
        last_name="Ahmadi",
        user_name=user_name,
        is_active=is_active,
    )


def create_refresh_token(user):
    return str(RefreshToken.for_user(user))


# ==================================================
# Register
# ==================================================

class TestRegisterCreateApiView:

    url = "account:api-v1:register"

    def setup_method(self):
        self.client = APIClient()

    def get_data(self, **kwargs):
        data = {
            "phone": "09123456789",
            "user_name": "ali",
            "first_name": "Ali",
            "last_name": "Ahmadi",
            "password": "Test12345!",
            "password_confirm": "Test12345!",
        }
        data.update(kwargs)
        return data

    def test_register_success(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(),
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(phone="09123456789").exists()

    def test_register_password_mismatch(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(password_confirm="Different123!"),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_phone(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(phone="123"),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(
                password="123",
                password_confirm="123",
            ),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_phone(self):
        create_user()

        response = self.client.post(
            reverse(self.url),
            self.get_data(),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_username(self):
        create_user()

        response = self.client.post(
            reverse(self.url),
            self.get_data(
                phone="09987654321",
                user_name="ali",
            ),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authenticated_user_cannot_register(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse(self.url),
            self.get_data(
                phone="09987654321",
                user_name="another_user",
            ),
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ==================================================
# Login
# ==================================================

class TestCustomTokenObtainPairView:

    url = "account:api-v1:login"

    def setup_method(self):
        self.client = APIClient()
        self.user = create_user()

    def test_login_success(self):
        response = self.client.post(
            reverse(self.url),
            {
                "phone": self.user.phone,
                "password": "Test12345!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse(self.url),
            {
                "phone": self.user.phone,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unknown_phone(self):
        response = self.client.post(
            reverse(self.url),
            {
                "phone": "09111111111",
                "password": "Test12345!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_inactive_user_cannot_login(self):
        inactive_user = create_user(
            phone="09111111111",
            user_name="inactive_user",
            is_active=False,
        )

        response = self.client.post(
            reverse(self.url),
            {
                "phone": inactive_user.phone,
                "password": "Test12345!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_cannot_login(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse(self.url),
            {
                "phone": self.user.phone,
                "password": "Test12345!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ==================================================
# Logout
# ==================================================

class TestLogoutApiView:

    url = "account:api-v1:logout"

    def setup_method(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_logout_success(self):
        refresh = create_refresh_token(self.user)

        response = self.client.post(
            reverse(self.url),
            {"refresh": refresh},
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_without_refresh(self):
        response = self.client.post(
            reverse(self.url),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_invalid_refresh(self):
        response = self.client.post(
            reverse(self.url),
            {"refresh": "invalid-token"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_anonymous_user_cannot_logout(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================================================
# Change password
# ==================================================

class TestPasswordChangeApiView:

    url = "account:api-v1:change-password"

    def setup_method(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def get_data(self, **kwargs):
        data = {
            "old_password": "Test12345!",
            "new_password": "NewPassword123!",
            "new_password_confirm": "NewPassword123!",
        }
        data.update(kwargs)
        return data

    def test_change_password_success(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(),
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()
        assert self.user.check_password("NewPassword123!")

    def test_change_password_wrong_old_password(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(old_password="WrongPassword123!"),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.user.refresh_from_db()
        assert self.user.check_password("Test12345!")

    def test_change_password_mismatch(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(new_password_confirm="Different123!"),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_weak_password(self):
        response = self.client.post(
            reverse(self.url),
            self.get_data(
                new_password="123",
                new_password_confirm="123",
            ),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_anonymous_user_cannot_change_password(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            self.get_data(),
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================================================
# Forgot password
# ==================================================

class TestForgotPasswordApiView:

    url = "account:api-v1:forgot-password"

    @patch("account.api.v1.views.send_otp_code_task.delay")
    def test_forgot_password_success(self, mock_task):
        user = create_user()
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {"phone": user.phone},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert PasswordResetOTPCode.objects.filter(user=user).exists()
        mock_task.assert_called_once()

    def test_forgot_password_unknown_phone(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {"phone": "09111111111"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_forgot_password_invalid_phone(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {"phone": "123"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ==================================================
# Verify password-reset OTP
# ==================================================

class TestVerifyOTPApiView:

    url = "account:api-v1:verify"

    def setup_method(self):
        self.user = create_user()
        self.client = APIClient()

    def create_otp(self):
        return PasswordResetOTPCode.generate_otp(self.user)

    def test_verify_otp_success(self):
        code = self.create_otp()

        response = self.client.post(
            reverse(self.url),
            {
                "phone": self.user.phone,
                "otp_code": code,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "reset_token" in response.data

    def test_verify_otp_wrong_code(self):
        self.create_otp()

        response = self.client.post(
            reverse(self.url),
            {
                "phone": self.user.phone,
                "otp_code": "000000",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_otp_expired(self):
        code = self.create_otp()

        PasswordResetOTPCode.objects.filter(
            user=self.user,
            otp_code=code,
        ).update(
            created_date=timezone.now() - timedelta(minutes=3)
        )

        response = self.client.post(
            reverse(self.url),
            {
                "phone": self.user.phone,
                "otp_code": code,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_otp_unknown_phone(self):
        response = self.client.post(
            reverse(self.url),
            {
                "phone": "09111111111",
                "otp_code": "123456",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ==================================================
# Reset password
# ==================================================


class TestResetPasswordApiView:
    url = "account:api-v1:reset-password"

    def setup_method(self):
        self.client = APIClient()
        self.user = create_user()

    def authenticate_with_reset_token(self):
        token = str(PasswordResetToken.for_user(self.user))
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    def get_data(self, **kwargs):
        data = {
            "new_password": "NewPassword123!",
            "new_password_confirm": "NewPassword123!",
        }
        data.update(kwargs)
        return data

    def test_reset_password_success(self):
        self.authenticate_with_reset_token()

        response = self.client.post(
            reverse(self.url),
            self.get_data(),
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()
        assert self.user.check_password("NewPassword123!")

    def test_reset_password_mismatch(self):
        self.authenticate_with_reset_token()

        response = self.client.post(
            reverse(self.url),
            self.get_data(
                new_password_confirm="DifferentPassword123!"
            ),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_weak_password(self):
        self.authenticate_with_reset_token()

        response = self.client.post(
            reverse(self.url),
            self.get_data(
                new_password="123",
                new_password_confirm="123",
            ),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST



# ==================================================
# Request phone-change OTP
# ==================================================

class TestPhoneChangeApiView:

    url = "account:api-v1:phone-change"

    def setup_method(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("account.api.v1.views.send_otp_code_task.delay")
    def test_phone_change_success(self, mock_task):
        new_phone = "09987654321"

        response = self.client.post(
            reverse(self.url),
            {"new_phone": new_phone},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert PhoneResetOTP.objects.filter(
            user=self.user,
            new_phone=new_phone,
        ).exists()
        mock_task.assert_called_once()

        self.user.refresh_from_db()
        assert self.user.phone == "09123456789"

    def test_phone_change_invalid_phone(self):
        response = self.client.post(
            reverse(self.url),
            {"new_phone": "123"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_change_same_phone(self):
        response = self.client.post(
            reverse(self.url),
            {"new_phone": self.user.phone},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_change_duplicate_phone(self):
        create_user(
            phone="09987654321",
            user_name="another_user",
        )

        response = self.client.post(
            reverse(self.url),
            {"new_phone": "09987654321"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_anonymous_user_cannot_change_phone(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {"new_phone": "09987654321"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================================================
# Verify phone-change OTP
# ==================================================

class TestVerifyPhoneChangeOTPApiView:

    url = "account:api-v1:phone-verify"

    def setup_method(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def create_phone_otp(self, new_phone):
        return PhoneResetOTP.generate_otp(
            self.user,
            new_phone=new_phone,
        )

    def get_data(self, new_phone, otp_code, refresh):
        return {
            "new_phone": new_phone,
            "otp_code": otp_code,
            "refresh": refresh,
        }

    def test_verify_phone_success(self):
        new_phone = "09987654321"
        code = self.create_phone_otp(new_phone)
        refresh = create_refresh_token(self.user)

        response = self.client.post(
            reverse(self.url),
            self.get_data(new_phone, code, refresh),
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()
        assert self.user.phone == new_phone

        otp = PhoneResetOTP.objects.get(
            user=self.user,
            new_phone=new_phone,
            otp_code=code,
        )
        assert otp.is_used is True

    def test_verify_phone_wrong_otp(self):
        new_phone = "09987654321"
        self.create_phone_otp(new_phone)
        refresh = create_refresh_token(self.user)

        response = self.client.post(
            reverse(self.url),
            self.get_data(new_phone, "000000", refresh),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.user.refresh_from_db()
        assert self.user.phone == "09123456789"

    def test_verify_phone_expired_otp(self):
        new_phone = "09987654321"
        code = self.create_phone_otp(new_phone)

        PhoneResetOTP.objects.filter(
            user=self.user,
            new_phone=new_phone,
            otp_code=code,
        ).update(
            created_date=timezone.now() - timedelta(minutes=3)
        )

        refresh = create_refresh_token(self.user)

        response = self.client.post(
            reverse(self.url),
            self.get_data(new_phone, code, refresh),
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_anonymous_user_cannot_verify_phone(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {
                "new_phone": "09987654321",
                "otp_code": "123456",
                "refresh": "invalid-token",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================================================
# Deactivate account
# ==================================================

class TestDeactivateAccountApiView:

    url = "account:api-v1:deactivate"

    def setup_method(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_deactivate_account_success(self):
        refresh = create_refresh_token(self.user)

        response = self.client.post(
            reverse(self.url),
            {"refresh": refresh},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()
        assert self.user.is_active is False

    def test_deactivate_account_without_refresh(self):
        response = self.client.post(
            reverse(self.url),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.user.refresh_from_db()
        assert self.user.is_active is True

    def test_deactivate_account_invalid_refresh(self):
        response = self.client.post(
            reverse(self.url),
            {"refresh": "invalid-token"},
            format="json",
        )

        # ویوی فعلی باید TokenError را مدیریت کند تا این تست پاس شود.
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_anonymous_user_cannot_deactivate_account(self):
        client = APIClient()

        response = client.post(
            reverse(self.url),
            {"refresh": "invalid-token"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED