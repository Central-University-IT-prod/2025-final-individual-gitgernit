import uuid

import dishka

from app.core.domain.advertiser.entities.entities import Advertiser
from app.core.domain.advertiser.entities.repositories import AdvertiserRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryAdvertiserRepository(AdvertiserRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_advertiser(
        self,
        advertiser: Advertiser,
        *,
        overwrite: bool = False,
    ) -> Advertiser:
        existing_index = next(
            (
                i
                for i, adv in enumerate(self._storage.advertisers)
                if adv.id == advertiser.id
            ),
            None,
        )

        if existing_index is not None:
            if overwrite:
                self._storage.advertisers[existing_index] = advertiser
                return advertiser
            return self._storage.advertisers[existing_index]

        self._storage.advertisers.append(advertiser)
        return advertiser

    async def get_advertiser(self, advertiser_id: uuid.UUID) -> Advertiser | None:
        return next(
            (adv for adv in self._storage.advertisers if adv.id == advertiser_id),
            None,
        )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryAdvertiserRepository, provides=AdvertiserRepository)
