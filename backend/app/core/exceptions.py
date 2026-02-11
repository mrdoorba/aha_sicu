"""Custom exceptions for the application."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class AuthException(AppException):
    """Authentication related exceptions."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(code=code, detail=detail, status_code=401)


class SyncException(AppException):
    """Sync-related exceptions."""

    def __init__(self, code: str, detail: str, status_code: int = 500) -> None:
        super().__init__(code=code, detail=detail, status_code=status_code)


class UploadException(AppException):
    """Upload-related exceptions."""

    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        super().__init__(code=code, detail=detail, status_code=status_code)


class CalculatorException(AppException):
    """Calculator-related exceptions."""

    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        super().__init__(code=code, detail=detail, status_code=status_code)
