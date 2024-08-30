from fastapi import HTTPException, status


class IncorrectPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Incorrect password"},
        )


class IncorrectAdminKeyException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": f"Incorrect admin-create key"},
        )


class UserEmailNotFoundException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": f"User with email {email} does not exist"},
        )


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class UserAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": f"User with email {email} already exists"},
        )


class UserWrongCodeException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": f"Wrong code for {email}"},
        )


class UserFeedbackStarsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Stars must be between 1 and 5"},
        )


class UserNotSubscribedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "You are not subscribed"},
        )


class UserWithVkNotFoundException(HTTPException):
    def __init__(self, uid: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": f"User with vk {uid} does not exist"},
        )


class UserWithGoogleNotFoundException(HTTPException):
    def __init__(self, uid: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": f"User with google {uid} does not exist"},
        )


class AchievementAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Achievement already exists"
        )


class AchievementNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Achievement not found"},
        )


class AchievementDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Achievement does not exist"
        )


class AdminAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": f"Admin with email {email} already exists"},
        )


class AdminNotFoundException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": f"Admin with email {email} does not exist"},
        )


class SubscriptionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Subscription do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )


class TopicNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Topic do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )


class SubTopicNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Subtopic do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )


class SubscriptionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Subscription do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )
