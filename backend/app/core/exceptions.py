from fastapi import HTTPException, status

class DataSentinelException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class EntityNotFoundException(DataSentinelException):
    def __init__(self, entity_name: str, entity_id: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with ID '{entity_id}' not found."
        )

class ValidationException(DataSentinelException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class AuthenticationException(DataSentinelException):
    def __init__(self, detail: str = "Invalid credentials or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class AuthorizationException(DataSentinelException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class FileProcessingException(DataSentinelException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
