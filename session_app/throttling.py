from rest_framework.throttling import UserRateThrottle


class AnonRateThrottle(UserRateThrottle):
    scope = "anon"


class UserRateThrottle(UserRateThrottle):
    scope = "user"


class BurstRateThrottle(UserRateThrottle):
    scope = "burst"


class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"


class LoginRateThrottle(UserRateThrottle):
    scope = "login"


class RegisterRateThrottle(UserRateThrottle):
    scope = "register"


class ReserveSeatThrottle(UserRateThrottle):
    scope = "reserve"
