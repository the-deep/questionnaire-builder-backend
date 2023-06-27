from enum import Enum, auto, unique
from django.db import models

from utils.common import get_queryset_for_model
from apps.common.models import UserResource
from apps.user.models import User


class ProjectMembership(models.Model):
    class Role(models.IntegerChoices):
        ADMIN = 0, 'Admin'
        MEMBER = 1, 'Member'

    member = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.MEMBER)

    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='added_project_memberships',
    )

    member_id: int
    project_id: int
    added_by_id: int

    class Meta:
        unique_together = ('member', 'project')

    def __str__(self):
        return '{} @ {}'.format(str(self.member), self.project.title)

    @property
    def member__id(self):
        return self.member_id


class Project(UserResource):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(
        User,
        blank=True,
        through_fields=('project', 'member'),
        through='ProjectMembership',
    )

    @unique
    class Permission(Enum):
        # Project
        UPDATE_PROJECT = auto()
        UPDATE_MEMBERSHIPS = auto()
        # Questionnaire
        VIEW_QUESTIONNAIRE = auto()
        CREATE_QUESTIONNAIRE = auto()
        UPDATE_QUESTIONNAIRE = auto()
        DELETE_QUESTIONNAIRE = auto()

    @property
    def get_permissions(cls) -> dict[ProjectMembership.Role, list[Permission]]:
        return {
            ProjectMembership.Role.ADMIN: [
                permission
                for permission in cls.Permission
            ],
            ProjectMembership.Role.MEMBER: [
                cls.Permission.VIEW_QUESTIONNAIRE,
                cls.Permission.CREATE_QUESTIONNAIRE,
                cls.Permission.UPDATE_QUESTIONNAIRE,
                cls.Permission.DELETE_QUESTIONNAIRE,
            ],
        }

    def get_permissions_for_user(self, user: User):
        # XXX: N+1
        membership = ProjectMembership.objects.filter(
            member=user,
            project=self,
        ).first()
        if membership:
            return self.get_permissions.get(membership.role, [])
        return []

    @classmethod
    def get_for(cls, user, queryset=None):
        current_user_role_subquery = models.Subquery(
            ProjectMembership.objects.filter(
                project=models.OuterRef('pk'),
                member=user,
            ).order_by('role').values('role')[:1],
            output_field=models.CharField(),
        )

        return get_queryset_for_model(cls, queryset=queryset).annotate(
            # For using within query filters
            current_user_role=current_user_role_subquery,
        ).exclude(current_user_role__isnull=True)
