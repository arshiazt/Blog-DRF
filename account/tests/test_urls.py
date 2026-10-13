
import pytest
from django.urls import reverse, resolve

from account.api.v1 import views

pytestmark = pytest.mark.django_db

class TestAccountURLs:
    def test_api_v1_urls(self):
        url = reverse("account:api-v1:register")
        assert url == "/account/api/v1/register/"

        match = resolve(url)
        assert match.view_name == "account:api-v1:register"

class TestAPIV1URLs:
    def test_register_url(self):
        url = reverse("account:api-v1:register")
        assert url == "/account/api/v1/register/"
        assert resolve(url).func.view_class == views.RegisterCreateApiView

    def test_login_url(self):
        url = reverse("account:api-v1:login")
        assert url == "/account/api/v1/login/"
        assert resolve(url).func.view_class == views.CustomTokenObtainPairView

    def test_logout_url(self):
        url = reverse("account:api-v1:logout")
        assert url == "/account/api/v1/logout/"
        assert resolve(url).func.view_class == views.LogoutApiView

    def test_jwt_refresh_url(self):
        url = reverse("account:api-v1:jwt-refresh")
        assert url == "/account/api/v1/jwt/refresh/"

    def test_jwt_verify_url(self):
        url = reverse("account:api-v1:jwt-verify")
        assert url == "/account/api/v1/jwt/verify/"

    def test_change_password_url(self):
        url = reverse("account:api-v1:change-password")
        assert url == "/account/api/v1/change-password/"
        assert resolve(url).func.view_class == views.PasswordChangeApiView

    def test_forgot_password_url(self):
        url = reverse("account:api-v1:forgot-password")
        assert url == "/account/api/v1/forgot-password/"
        assert resolve(url).func.view_class == views.ForgotPasswordApiView

    def test_verify_otp_url(self):
        url = reverse("account:api-v1:verify")
        assert url == "/account/api/v1/verify-otp/"
        assert resolve(url).func.view_class == views.VerifyOTPApiView

    def test_reset_password_url(self):
        url = reverse("account:api-v1:reset-password")
        assert url == "/account/api/v1/reset-password/"
        assert resolve(url).func.view_class == views.ResetPasswordApiView

    def test_change_phone_url(self):
        url = reverse("account:api-v1:phone-change")
        assert url == "/account/api/v1/change-phone/"
        assert resolve(url).func.view_class == views.PhoneChangeApiView

    def test_verify_phone_url(self):
        url = reverse("account:api-v1:phone-verify")
        assert url == "/account/api/v1/verify-phone/"
        assert resolve(url).func.view_class == views.VerifyPhoneChangeOTPApiView

    def test_deactivate_url(self):
        url = reverse("account:api-v1:deactivate")
        assert url == "/account/api/v1/deactivate/"
        assert resolve(url).func.view_class == views.DeactivateAccountApiView