import typing
import strawberry
import strawberry_django
from strawberry.types import Info

from utils.common import get_queryset_for_model
from utils.strawberry.paginations import CountList, pagination_field
from apps.common.types import ClientIdMixin

from .models import Project, ProjectMembership
from .filters import ProjectMembershipFilter
from .enums import ProjectMembershipRoleTypeEnum


@strawberry_django.type(ProjectMembership)
class ProjectMembershipType(ClientIdMixin):
    id: strawberry.ID
    role: ProjectMembershipRoleTypeEnum
    joined_at: strawberry.auto

    member_id: strawberry.ID

    # @strawberry.field
    # def member_id(self) -> strawberry.ID:
    #     return self.member_id

    @strawberry.field
    def added_by_id(self) -> strawberry.ID | None:
        return self.added_by_id

    def get_queryset(self, queryset, info: Info):
        queryset = get_queryset_for_model(ProjectMembership, queryset=queryset)
        return queryset.filter(
            project=info.context.active_project.project,
        )


@strawberry_django.type(Project)
class ProjectType:
    id: strawberry.ID
    title: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto
    created_by: strawberry.auto
    modified_by: strawberry.auto

    members: CountList[ProjectMembershipType] = pagination_field(
        pagination=True,
        filters=ProjectMembershipFilter,
    )

    @strawberry.field
    def current_user_role(self) -> typing.Optional[ProjectMembershipRoleTypeEnum]:
        # Annotated by Project.get_for
        return getattr(self, 'current_user_role', None)

    def get_queryset(self, queryset, info: Info):
        return Project.get_for(
            info.context.request.user,
            queryset=queryset,
        )
