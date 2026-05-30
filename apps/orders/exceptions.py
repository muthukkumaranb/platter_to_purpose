from apps.exceptions import AppException


class FoodAlreadyClaimedException(AppException):
    default_detail = "This food has already been claimed."
    default_code = "food_already_claimed"


class OrderWithdrawalWindowExpiredException(AppException):
    default_detail = "The cancellation window (5 minutes) has expired."
    default_code = "withdrawal_window_expired"


class InvalidPickupTokenException(AppException):
    default_detail = "The pickup verification token is invalid."
    default_code = "invalid_pickup_token"


class UnauthorizedOrderActionException(AppException):
    default_detail = "You are not authorized to perform this action on the order."
    default_code = "unauthorized_order_action"


class OrderAlreadyCompletedException(AppException):
    default_detail = "This order has already been completed."
    default_code = "order_already_completed"
