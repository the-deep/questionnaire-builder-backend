import strawberry
from dataclasses import dataclass
from strawberry.django.views import AsyncGraphQLView
from strawberry.django.context import StrawberryDjangoContext

from apps.user import queries as user_queries, mutations as user_mutations

from .permissions import IsAuthenticated
from .dataloaders import GlobalDataLoader


@dataclass
class GraphQLContext(StrawberryDjangoContext):
    dl: GlobalDataLoader


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, *args, **kwargs) -> GraphQLContext:
        return GraphQLContext(
            *args,
            **kwargs,
            dl=GlobalDataLoader(),
        )


@strawberry.type
class PublicQuery(
    user_queries.PublicQuery,
):
    id: strawberry.ID = strawberry.ID('public')


@strawberry.type
class PrivateQuery(
    user_queries.PrivateQuery,
):
    id: strawberry.ID = strawberry.ID('private')


@strawberry.type
class PublicMutation(
    user_mutations.PublicMutation,
):
    id: strawberry.ID = strawberry.ID('public')


@strawberry.type
class PrivateMutation(
    user_mutations.PrivateMutation,
):
    id: strawberry.ID = strawberry.ID('private')


@strawberry.type
class Query:
    public: PublicQuery = strawberry.field(resolver=lambda: PublicQuery())
    private: PrivateQuery = strawberry.field(permission_classes=[IsAuthenticated], resolver=lambda: PrivateQuery())


@strawberry.type
class Mutation:
    public: PublicMutation = strawberry.field(resolver=lambda: PublicMutation())
    private: PrivateMutation = strawberry.field(permission_classes=[IsAuthenticated], resolver=lambda: PrivateMutation())


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
