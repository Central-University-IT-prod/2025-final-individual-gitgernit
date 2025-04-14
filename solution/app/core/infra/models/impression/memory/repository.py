import uuid

import dishka

from app.core.domain.feed.entities.entities import CampaignImpression
from app.core.domain.feed.entities.repositories import ImpressionsRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryImpressionsRepository(ImpressionsRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_impression(
        self,
        impression: CampaignImpression,
    ) -> CampaignImpression:
        if impression.id is None:
            impression.id = uuid.uuid4()
        self._storage.impressions.append(impression)
        return impression

    async def get_campaign_impressions(
        self,
        campaign_id: uuid.UUID,
        day: int | None = None,
    ) -> list[CampaignImpression]:
        return [
            imp
            for imp in self._storage.impressions
            if imp.campaign_id == campaign_id and (day is None or imp.day == day)
        ]


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryImpressionsRepository, provides=ImpressionsRepository)
