class APEXException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(APEXException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class UnauthorizedError(APEXException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(APEXException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class DatabaseError(APEXException):
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status_code=500)
