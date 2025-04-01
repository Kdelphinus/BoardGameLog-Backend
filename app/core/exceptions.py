from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    """HTTP_400_BAD_REQUEST"""

    def __init__(self, detail="Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class CredentialsException(HTTPException):
    """HTTP_401_UNAUTHORIZED"""

    def __init__(self, detail="Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(HTTPException):
    """HTTP_404_NOT_FOUND"""

    def __init__(self, detail="Could not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class NotAcceptableException(HTTPException):
    """HTTP_406_NOT_ACCEPTABLE"""

    def __init__(self, detail="Not acceptable"):
        super().__init__(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=detail)


class ConflictException(HTTPException):
    """HTTP_409_CONFLICT"""

    def __init__(self, detail="Data already exists."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityException(HTTPException):
    """HTTP_422_UNPROCESSABLE_ENTITY"""

    def __init__(self, detail="Unprocessable entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
