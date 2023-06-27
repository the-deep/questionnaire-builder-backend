import strawberry
from strawberry.types import Info

from main.caches import local_cache
from apps.common.serializers import TempClientIdMixin


@strawberry.type
class ClientIdMixin:

    @strawberry.field
    def client_id(self, info: Info) -> str:
        self.id: int
        # NOTE: We should always provide non-null client_id
        return (
            getattr(self, 'client_id', None) or
            local_cache.get(TempClientIdMixin.get_cache_key(self, info.context)) or
            str(self.id)
        )
