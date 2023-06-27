import strawberry
from strawberry.types import Info

from utils.strawberry.mutations import MutationResponseType, BulkMutationResponseType, ModelMutation

from apps.questionnaire import mutations as questionnaire_mutations
from .models import Project, ProjectMembership
from .serializers import (
    ProjectSerializer,
    ProjectMembershipBulkSerializer,
)
from .types import ProjectType, ProjectMembershipType

ProjectMutation = ModelMutation('Project', ProjectSerializer)
ProjectMembershipBulkMutation = ModelMutation('ProjectMembership', ProjectMembershipBulkSerializer)


# NOTE: strawberry_django.type doesn't let use arguments in the field
@strawberry.type
class ProjectScopeMutation(
    questionnaire_mutations.ProjectScopeMutation,
):
    id: strawberry.ID

    @strawberry.mutation
    async def update_project(
        self,
        data: ProjectMutation.InputType,
        info: Info,
    ) -> MutationResponseType[ProjectType]:
        return await ProjectMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_PROJECT,
            info.context.active_project.project,
        )

    @strawberry.mutation
    async def update_memberships(
        self,
        items: list[ProjectMembershipBulkMutation.PartialInputType] | None,
        data_delete_ids: list[strawberry.ID] | None,
        info: Info,
    ) -> BulkMutationResponseType[ProjectMembershipType]:
        queryset = ProjectMembership.objects.filter(project=info.context.active_project.project)
        return await ProjectMembershipBulkMutation.handle_bulk_mutation(
            queryset,
            items,
            data_delete_ids,
            info,
            Project.Permission.UPDATE_MEMBERSHIPS,
        )


@strawberry.type
class PrivateMutation:
    @strawberry.mutation
    async def create_project(
        self,
        data: ProjectMutation.InputType,
        info: Info,
    ) -> MutationResponseType[ProjectType]:
        return await ProjectMutation.handle_create_mutation(
            data,
            info,
            Project.Permission.UPDATE_PROJECT,
        )

    @strawberry.field
    async def project_scope(self, info: Info, pk: strawberry.ID) -> ProjectScopeMutation | None:
        project = await Project\
            .get_for(info.context.request.user)\
            .filter(pk=pk)\
            .afirst()
        if project:
            await info.context.set_active_project(project)
        return project
