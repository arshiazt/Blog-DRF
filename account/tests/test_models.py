import pytest
from django.db import IntegrityError, transaction
from account.models import (
    User,
    PasswordResetOTPCode,
    PhoneResetOTP,
)

class TestUserManager:

    @pytest.mark.django_db
    def test_create_user(self):
        user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        assert user.phone == "09123456789"
        assert user.first_name == "Ali"
        assert user.last_name == "Ahmadi"
        assert user.user_name == "ali"

    @pytest.mark.django_db
    def test_create_user_password(self):
        user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        assert user.check_password("Test12345!")
        assert not user.check_password("WrongPassword")

    @pytest.mark.django_db
    def test_create_user_default_fields(self):
        user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

        assert user.is_staff is False
        assert user.is_active is True
        assert user.is_superuser is False

    def test_create_user_without_phone(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                phone="",
                password="Test12345!",
                first_name="Ali",
                last_name="Ahmadi",
                user_name="ali",
            )

    def test_create_user_without_first_name(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                phone="09123456789",
                password="Test12345!",
                first_name="",
                last_name="Ahmadi",
                user_name="ali",
            )

    def test_create_user_without_last_name(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                phone="09123456789",
                password="Test12345!",
                first_name="Ali",
                last_name="",
                user_name="ali",
            )

    def test_create_user_without_user_name(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                phone="09123456789",
                password="Test12345!",
                first_name="Ali",
                last_name="Ahmadi",
                user_name="",
            )

    @pytest.mark.django_db
    def test_create_superuser(self):
        user = User.objects.create_superuser(
            phone="09123456789",
            password="Test12345!",
            first_name="Admin",
            last_name="User",
            user_name="admin",
        )

        assert user.is_staff is True
        assert user.is_active is True
        assert user.is_superuser is True

    def test_create_superuser_without_staff(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                phone="09123456789",
                password="Test12345!",
                first_name="Admin",
                last_name="User",
                user_name="admin",
                is_staff=False,
            )

    def test_create_superuser_without_active(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                phone="09123456789",
                password="Test12345!",
                first_name="Admin",
                last_name="User",
                user_name="admin",
                is_active=False,
            )

    def test_create_superuser_without_superuser(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                phone="09123456789",
                password="Test12345!",
                first_name="Admin",
                last_name="User",
                user_name="admin",
                is_superuser=False,
            )


@pytest.mark.django_db
class TestUserModel:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

    def test_str(self):
        assert str(self.user) == "09123456789"

    def test_username_field(self):
        assert User.USERNAME_FIELD == "phone"

    def test_required_fields(self):
        assert User.REQUIRED_FIELDS == [
            "first_name",
            "last_name",
            "user_name",
        ]

    def test_phone_is_unique(self):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    phone="09123456789",
                    password="Test12345!",
                    first_name="Reza",
                    last_name="Ahmadi",
                    user_name="reza",
                )

    def test_user_name_is_unique(self):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    phone="09123456780",
                    password="Test12345!",
                    first_name="Reza",
                    last_name="Ahmadi",
                    user_name="ali",
                )

    def test_user_is_active_by_default(self):
        assert self.user.is_active is True

    def test_user_is_staff_false_by_default(self):
        assert self.user.is_staff is False


@pytest.mark.django_db
class TestPasswordResetOTPCode:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

    def test_generate_otp_returns_string(self):
        otp = PasswordResetOTPCode.generate_otp(self.user)

        assert isinstance(otp, str)

    def test_generate_otp_has_six_digits(self):
        otp = PasswordResetOTPCode.generate_otp(self.user)

        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_creates_database_record(self):
        PasswordResetOTPCode.generate_otp(self.user)

        assert PasswordResetOTPCode.objects.filter(
            user=self.user
        ).count() == 1

    def test_generated_otp_is_saved_correctly(self):
        otp = PasswordResetOTPCode.generate_otp(self.user)

        otp_object = PasswordResetOTPCode.objects.get(
            user=self.user,
            otp_code=otp,
        )

        assert otp_object.otp_code == otp

    def test_generated_otp_is_unused(self):
        otp = PasswordResetOTPCode.generate_otp(self.user)

        otp_object = PasswordResetOTPCode.objects.get(
            user=self.user,
            otp_code=otp,
        )

        assert otp_object.is_used is False

    def test_generated_otp_has_created_date(self):
        otp = PasswordResetOTPCode.generate_otp(self.user)

        otp_object = PasswordResetOTPCode.objects.get(
            user=self.user,
            otp_code=otp,
        )

        assert otp_object.created_date is not None

    def test_otp_is_related_to_correct_user(self):
        otp = PasswordResetOTPCode.generate_otp(self.user)

        otp_object = PasswordResetOTPCode.objects.get(
            otp_code=otp,
        )

        assert otp_object.user == self.user


@pytest.mark.django_db
class TestPhoneResetOTP:

    def setup_method(self):
        self.user = User.objects.create_user(
            phone="09123456789",
            password="Test12345!",
            first_name="Ali",
            last_name="Ahmadi",
            user_name="ali",
        )

    def test_generate_otp_returns_string(self):
        otp = PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        assert isinstance(otp, str)

    def test_generate_otp_has_six_digits(self):
        otp = PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_creates_database_record(self):
        PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        assert PhoneResetOTP.objects.filter(
            user=self.user
        ).count() == 1

    def test_generated_otp_is_saved_correctly(self):
        otp = PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        otp_object = PhoneResetOTP.objects.get(
            user=self.user,
            otp_code=otp,
        )

        assert otp_object.otp_code == otp

    def test_generated_otp_is_unused(self):
        otp = PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        otp_object = PhoneResetOTP.objects.get(
            user=self.user,
            otp_code=otp,
        )

        assert otp_object.is_used is False

    def test_generated_otp_has_created_date(self):
        otp = PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        otp_object = PhoneResetOTP.objects.get(
            user=self.user,
            otp_code=otp,
        )

        assert otp_object.created_date is not None

    def test_otp_is_related_to_correct_user(self):
        otp = PhoneResetOTP.generate_otp(
            self.user,
            "09987654321",
        )

        otp_object = PhoneResetOTP.objects.get(
            otp_code=otp,
        )

        assert otp_object.user == self.user

    def test_new_phone_is_saved_correctly(self):
        new_phone = "09987654321"

        otp = PhoneResetOTP.generate_otp(
            self.user,
            new_phone,
        )

        otp_object = PhoneResetOTP.objects.get(
            otp_code=otp,
        )

        assert otp_object.new_phone == new_phone