import pytest

from datetime import timedelta
from types import SimpleNamespace

from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from account.models import (
    User,
    PasswordResetOTPCode,
    PhoneResetOTP,
)

from account.api.v1.serializers import (
    RegistrationSerializer,
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    PhoneChangeSerializer,
    VerifyPhoneChangeOTPSerializer,
    DeactivateAccountSerializer,
)


@pytest.mark.django_db
class TestRegistrationSerializer:

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

    def test_valid_registration(self):
        serializer = RegistrationSerializer(data=self.get_data())

        assert serializer.is_valid(), serializer.errors

    def test_create_user(self):
        serializer = RegistrationSerializer(data=self.get_data())
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()

        assert User.objects.filter(pk=user.pk).exists()
        assert user.phone == "09123456789"
        assert user.user_name == "ali"
        assert user.check_password("Test12345!")

    def test_password_confirm_is_not_saved(self):
        serializer = RegistrationSerializer(data=self.get_data())
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()

        assert not hasattr(user, "password_confirm")

    def test_passwords_do_not_match(self):
        serializer = RegistrationSerializer(
            data=self.get_data(password_confirm="Different123!")
        )

        assert not serializer.is_valid()
        assert "detail" in serializer.errors

    def test_phone_is_required(self):
        data = self.get_data()
        data.pop("phone")

        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_invalid_phone(self):
        serializer = RegistrationSerializer(
            data=self.get_data(phone="123")
        )

        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_password_is_required(self):
        data = self.get_data()
        data.pop("password")

        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_password_minimum_length(self):
        serializer = RegistrationSerializer(
            data=self.get_data(
                password="Ab1!",
                password_confirm="Ab1!",
            )
        )

        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_username_is_required(self):
        data = self.get_data()
        data.pop("user_name")

        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert "user_name" in serializer.errors

    def test_duplicate_phone(self):
        User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        serializer = RegistrationSerializer(
            data=self.get_data(user_name="another_user")
        )

        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_duplicate_username(self):
        User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        serializer = RegistrationSerializer(
            data=self.get_data(phone="09123456780")
        )

        assert not serializer.is_valid()
        assert "user_name" in serializer.errors


@pytest.mark.django_db
class TestCustomTokenObtainPairSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

    def test_token_contains_custom_fields(self):
        token = CustomTokenObtainPairSerializer.get_token(self.user)

        assert token["id"] == self.user.id
        assert token["phone"] == self.user.phone
        assert token["user_name"] == self.user.user_name
        assert token["is_staff"] == self.user.is_staff

    def test_valid_login(self):
        serializer = CustomTokenObtainPairSerializer(
            data={
                "phone": "09123456789",
                "password": "Test12345!",
            }
        )

        assert serializer.is_valid(), serializer.errors
        assert "access" in serializer.validated_data
        assert "refresh" in serializer.validated_data

    def test_invalid_password(self):
        serializer = CustomTokenObtainPairSerializer(
            data={
                "phone": "09123456789",
                "password": "WrongPassword123!",
            }
        )

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_nonexistent_user(self):
        serializer = CustomTokenObtainPairSerializer(
            data={
                "phone": "09111111111",
                "password": "Test12345!",
            }
        )

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_login_response_contains_user_info(self):
        serializer = CustomTokenObtainPairSerializer(
            data={
                "phone": "09123456789",
                "password": "Test12345!",
            }
        )

        assert serializer.is_valid(), serializer.errors

        user_data = serializer.validated_data["user"]

        assert user_data["id"] == self.user.id
        assert user_data["phone"] == self.user.phone
        assert user_data["user_name"] == self.user.user_name
        assert user_data["is_staff"] is False


@pytest.mark.django_db
class TestPasswordChangeSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        self.context = {
            "request": SimpleNamespace(user=self.user)
        }

    def get_data(self, **kwargs):
        data = {
            "old_password": "Test12345!",
            "new_password": "NewTest12345!",
            "new_password_confirm": "NewTest12345!",
        }
        data.update(kwargs)
        return data

    def test_valid_password_change(self):
        serializer = PasswordChangeSerializer(
            data=self.get_data(),
            context=self.context,
        )

        assert serializer.is_valid(), serializer.errors

    def test_wrong_old_password(self):
        serializer = PasswordChangeSerializer(
            data=self.get_data(old_password="WrongPassword123!"),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "old_password" in serializer.errors

    def test_new_passwords_do_not_match(self):
        serializer = PasswordChangeSerializer(
            data=self.get_data(
                new_password_confirm="Different123!"
            ),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_password_confirm" in serializer.errors

    def test_change_password(self):
        serializer = PasswordChangeSerializer(
            data=self.get_data(),
            context=self.context,
        )
        assert serializer.is_valid(), serializer.errors

        serializer.save()
        self.user.refresh_from_db()

        assert self.user.check_password("NewTest12345!")
        assert not self.user.check_password("Test12345!")

    def test_new_password_is_required(self):
        data = self.get_data()
        data.pop("new_password")

        serializer = PasswordChangeSerializer(
            data=data,
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_password" in serializer.errors


@pytest.mark.django_db
class TestForgotPasswordSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

    def test_valid_phone(self):
        serializer = ForgotPasswordSerializer(
            data={"phone": self.user.phone}
        )

        assert serializer.is_valid(), serializer.errors

    def test_nonexistent_phone(self):
        serializer = ForgotPasswordSerializer(
            data={"phone": "09111111111"}
        )

        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_invalid_phone(self):
        serializer = ForgotPasswordSerializer(
            data={"phone": "123"}
        )

        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_phone_is_required(self):
        serializer = ForgotPasswordSerializer(data={})

        assert not serializer.is_valid()
        assert "phone" in serializer.errors


@pytest.mark.django_db
class TestVerifyOTPSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        self.otp = PasswordResetOTPCode.objects.create(
            user=self.user,
            otp_code="123456",
        )

    def get_data(self, **kwargs):
        data = {
            "phone": self.user.phone,
            "otp_code": "123456",
        }
        data.update(kwargs)
        return data

    def test_valid_otp(self):
        serializer = VerifyOTPSerializer(data=self.get_data())

        assert serializer.is_valid(), serializer.errors

    def test_valid_otp_returns_user(self):
        serializer = VerifyOTPSerializer(data=self.get_data())
        assert serializer.is_valid(), serializer.errors

        assert serializer.validated_data["user"] == self.user

    def test_valid_otp_is_marked_as_used(self):
        serializer = VerifyOTPSerializer(data=self.get_data())
        assert serializer.is_valid(), serializer.errors

        self.otp.refresh_from_db()

        assert self.otp.is_used is True

    def test_invalid_otp(self):
        serializer = VerifyOTPSerializer(
            data=self.get_data(otp_code="999999")
        )

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_used_otp(self):
        self.otp.is_used = True
        self.otp.save(update_fields=["is_used"])

        serializer = VerifyOTPSerializer(data=self.get_data())

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_expired_otp(self):
        PasswordResetOTPCode.objects.filter(
            pk=self.otp.pk
        ).update(
            created_date=timezone.now() - timedelta(minutes=3)
        )

        serializer = VerifyOTPSerializer(data=self.get_data())

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_nonexistent_phone(self):
        serializer = VerifyOTPSerializer(
            data=self.get_data(phone="09111111111")
        )

        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_invalid_otp_format(self):
        serializer = VerifyOTPSerializer(
            data=self.get_data(otp_code="abc")
        )

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors


@pytest.mark.django_db
class TestResetPasswordSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        self.context = {"user": self.user}

    def get_data(self, **kwargs):
        data = {
            "new_password": "NewTest12345!",
            "new_password_confirm": "NewTest12345!",
        }
        data.update(kwargs)
        return data

    def test_valid_data(self):
        serializer = ResetPasswordSerializer(
            data=self.get_data(),
            context=self.context,
        )

        assert serializer.is_valid(), serializer.errors

    def test_passwords_do_not_match(self):
        serializer = ResetPasswordSerializer(
            data=self.get_data(
                new_password_confirm="Different123!"
            ),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_password_confirm" in serializer.errors

    def test_password_minimum_length(self):
        serializer = ResetPasswordSerializer(
            data=self.get_data(
                new_password="Ab1!",
                new_password_confirm="Ab1!",
            ),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_password" in serializer.errors

    def test_reset_password(self):
        serializer = ResetPasswordSerializer(
            data=self.get_data(),
            context=self.context,
        )
        assert serializer.is_valid(), serializer.errors

        serializer.save()
        self.user.refresh_from_db()

        assert self.user.check_password("NewTest12345!")
        assert not self.user.check_password("Test12345!")

    def test_new_password_is_required(self):
        data = self.get_data()
        data.pop("new_password")

        serializer = ResetPasswordSerializer(
            data=data,
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_password" in serializer.errors


@pytest.mark.django_db
class TestPhoneChangeSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        self.context = {
            "request": SimpleNamespace(user=self.user)
        }

    def test_valid_new_phone(self):
        serializer = PhoneChangeSerializer(
            data={"new_phone": "09987654321"},
            context=self.context,
        )

        assert serializer.is_valid(), serializer.errors

    def test_same_phone_is_rejected(self):
        serializer = PhoneChangeSerializer(
            data={"new_phone": self.user.phone},
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_phone" in serializer.errors

    def test_phone_used_by_another_user_is_rejected(self):
        User.objects.create_user(
            phone="09987654321",
            password="Test12345!",
            first_name="Reza",
            last_name="Ahmadi",
            user_name="reza",
        )

        serializer = PhoneChangeSerializer(
            data={"new_phone": "09987654321"},
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_phone" in serializer.errors

    def test_invalid_phone(self):
        serializer = PhoneChangeSerializer(
            data={"new_phone": "123"},
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_phone" in serializer.errors

    def test_new_phone_is_required(self):
        serializer = PhoneChangeSerializer(
            data={},
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "new_phone" in serializer.errors


@pytest.mark.django_db
class TestVerifyPhoneChangeOTPSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        self.otp = PhoneResetOTP.objects.create(
            user=self.user,
            new_phone="09987654321",
            otp_code="123456",
        )

        self.context = {
            "request": SimpleNamespace(user=self.user)
        }

    def get_data(self, **kwargs):
        data = {
            "new_phone": "09987654321",
            "otp_code": "123456",
            "refresh": "test-refresh-token",
        }
        data.update(kwargs)
        return data

    def test_valid_data(self):
        serializer = VerifyPhoneChangeOTPSerializer(
            data=self.get_data(),
            context=self.context,
        )

        assert serializer.is_valid(), serializer.errors

    def test_valid_otp_returns_otp_object(self):
        serializer = VerifyPhoneChangeOTPSerializer(
            data=self.get_data(),
            context=self.context,
        )
        assert serializer.is_valid(), serializer.errors

        assert serializer.validated_data["otp"] == self.otp

    def test_invalid_otp(self):
        serializer = VerifyPhoneChangeOTPSerializer(
            data=self.get_data(otp_code="999999"),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_otp_for_another_phone_is_rejected(self):
        serializer = VerifyPhoneChangeOTPSerializer(
            data=self.get_data(new_phone="09111111111"),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_used_otp_is_rejected(self):
        self.otp.is_used = True
        self.otp.save(update_fields=["is_used"])

        serializer = VerifyPhoneChangeOTPSerializer(
            data=self.get_data(),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_expired_otp(self):
        PhoneResetOTP.objects.filter(
            pk=self.otp.pk
        ).update(
            created_date=timezone.now() - timedelta(minutes=3)
        )

        serializer = VerifyPhoneChangeOTPSerializer(
            data=self.get_data(),
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "otp_code" in serializer.errors

    def test_refresh_is_required(self):
        data = self.get_data()
        data.pop("refresh")

        serializer = VerifyPhoneChangeOTPSerializer(
            data=data,
            context=self.context,
        )

        assert not serializer.is_valid()
        assert "refresh" in serializer.errors


class TestDeactivateAccountSerializer:

    def test_valid_refresh_token(self):
        serializer = DeactivateAccountSerializer(
            data={"refresh": "test-refresh-token"}
        )

        assert serializer.is_valid(), serializer.errors

    def test_refresh_is_required(self):
        serializer = DeactivateAccountSerializer(data={})

        assert not serializer.is_valid()
        assert "refresh" in serializer.errors