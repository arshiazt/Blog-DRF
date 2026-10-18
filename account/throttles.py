from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class LoginThrottle(AnonRateThrottle):
    scope = "login"

class RegisterThrottle(AnonRateThrottle):
    scope = "register"

class LogoutThrottle(UserRateThrottle):
    scope = "logout"

class TokenRefreshThrottle(AnonRateThrottle):
    scope = "token_refresh"

class TokenVerifyThrottle(AnonRateThrottle):
    scope = "token_verify"