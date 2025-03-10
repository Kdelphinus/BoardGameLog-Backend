from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail="Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(HTTPException):
    def __init__(self, detail="Could not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class NotAcceptableException(HTTPException):
    def __init__(self, detail="Not acceptable"):
        super().__init__(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail="Data already exists."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityException(HTTPException):
    def __init__(self, detail="Unprocessable entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
