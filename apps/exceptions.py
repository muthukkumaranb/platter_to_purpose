class AppException(Exception):  # noqa: N818
    status_code = 400
    default_detail = "A system error occurred."
    default_code = "error"

    def __init__(self, detail=None, code=None, status_code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        if status_code:
            self.status_code = status_code

    def __str__(self):
        return f"[{self.code}] {self.detail}"
