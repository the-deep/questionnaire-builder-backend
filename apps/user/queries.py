import strawberry
import strawberry_django
from strawberry.types import Info

from asgiref.sync import sync_to_async

from .models import User
from .enums import OptEmailNotificationTypeEnum


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    first_name: strawberry.auto
    last_name: strawberry.auto


@strawberry_django.type(User)
class UserMeType(UserType):
    email: strawberry.auto
    email_opt_outs: list[OptEmailNotificationTypeEnum]


@strawberry.type
class PublicQuery:
    @strawberry.field
    @sync_to_async
    def me(self, info: Info) -> UserMeType | None:
        user = info.context.request.user
        if user.is_authenticated:
            return user


@strawberry.type
class PrivateQuery:
    user: UserType = strawberry_django.field()
