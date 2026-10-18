from types import SimpleNamespace

from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from account.throttles import (
    LoginThrottle,
    RegisterThrottle,
    LogoutThrottle,
    TokenRefreshThrottle,
    TokenVerifyThrottle,
    PasswordChangeThrottle,
    ForgotPasswordThrottle,
    VerifyOTPThrottle,
    ResetPasswordThrottle,
    PhoneChangeThrottle,
    VerifyPhoneChangeThrottle,
    DeactivateAccountThrottle,
)

class BaseThrottleTest:

    throttle_class = None
    authenticated = False
    test_rate = "2/min"

    def setup_method(self):
        cache.clear()

        self.factory = APIRequestFactory()
        self.throttle = self.throttle_class()

        # تعیین نرخ مخصوص تست
        self.throttle.rate = self.test_rate
        (
            self.throttle.num_requests,
            self.throttle.duration,
        ) = self.throttle.parse_rate(self.test_rate)

    def make_request(self):
        raw_request = self.factory.post(
            "/test/",
            REMOTE_ADDR="127.0.0.1",
        )

        raw_request.user = SimpleNamespace(
            is_authenticated=self.authenticated,
            pk=1 if self.authenticated else None,
        )

        return Request(raw_request)

    def test_request_limit(self):
        results = []

        for _ in range(3):
            request = self.make_request()
            results.append(
                self.throttle.allow_request(request, None)
            )

        assert results == [True, True, False]

class TestLoginThrottle(BaseThrottleTest):
    throttle_class = LoginThrottle

class TestRegisterThrottle(BaseThrottleTest):
    throttle_class = RegisterThrottle

class TestLogoutThrottle(BaseThrottleTest):
    throttle_class = LogoutThrottle
    authenticated = True

class TestTokenRefreshThrottle(BaseThrottleTest):
    throttle_class = TokenRefreshThrottle

class TestTokenVerifyThrottle(BaseThrottleTest):
    throttle_class = TokenVerifyThrottle

class TestPasswordChangeThrottle(BaseThrottleTest):
    throttle_class = PasswordChangeThrottle
    authenticated = True

class TestForgotPasswordThrottle(BaseThrottleTest):
    throttle_class = ForgotPasswordThrottle

class TestVerifyOTPThrottle(BaseThrottleTest):
    throttle_class = VerifyOTPThrottle

class TestResetPasswordThrottle(BaseThrottleTest):
    throttle_class = ResetPasswordThrottle

class TestPhoneChangeThrottle(BaseThrottleTest):
    throttle_class = PhoneChangeThrottle
    authenticated = True

class TestVerifyPhoneChangeThrottle(BaseThrottleTest):
    throttle_class = VerifyPhoneChangeThrottle
    authenticated = True

class TestDeactivateAccountThrottle(BaseThrottleTest):
    throttle_class = DeactivateAccountThrottle
    authenticated = True