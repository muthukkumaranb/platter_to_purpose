from apps.exceptions import AppException


class OnlyHotelsCanPostException(AppException):
    default_detail = "Only hotels can post food donations."
    default_code = "only_hotels_can_post"


class FoodPostNotFoundException(AppException):
    default_detail = "This food post does not exist."
    default_code = "food_post_not_found"


class FoodPostReservedException(AppException):
    default_detail = "This food post is currently reserved for orphanages."
    default_code = "food_post_reserved"
