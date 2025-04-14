import uuid

import dishka

from app.core.domain.campaign.entities.entities import Campaign, Gender
from app.core.domain.campaign.entities.repositories import CampaignRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryCampaignRepository(CampaignRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_campaign(
        self,
        campaign: Campaign,
        *,
        overwrite: bool = False,
    ) -> Campaign:
        existing_index = next(
            (i for i, c in enumerate(self._storage.campaigns) if c.id == campaign.id),
            None,
        )

        if existing_index is not None:
            if overwrite:
                self._storage.campaigns[existing_index] = campaign
                return campaign

            return self._storage.campaigns[existing_index]

        campaign.id = uuid.uuid4()

        self._storage.campaigns.append(campaign)
        return campaign

    async def get_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> Campaign | None:
        return next(
            (c for c in self._storage.campaigns if c.id == campaign_id),
            None,
        )

    async def delete_campaign(
        self,
        campaign_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> None:
        self._storage.campaigns = [
            c
            for c in self._storage.campaigns
            if not (c.id == campaign_id and c.advertiser_id == advertiser_id)
        ]

    async def get_advertiser_campaigns(
        self,
        advertiser_id: uuid.UUID,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Campaign]:
        campaigns = [
            c for c in self._storage.campaigns if c.advertiser_id == advertiser_id
        ]
        return campaigns[offset : (offset + limit) if limit is not None else None]

    async def get_targeted_campaigns(
        self,
        age: int,
        location: str,
        gender: Gender,
    ) -> list[Campaign]:
        return [
            c
            for c in self._storage.campaigns
            if c.targeting
            and (c.targeting.age_from is None or c.targeting.age_from <= age)
            and (c.targeting.age_to is None or c.targeting.age_to >= age)
            and (c.targeting.location is None or c.targeting.location == location)
            and (
                c.targeting.gender is None or c.targeting.gender in (gender, Gender.ALL)
            )
        ]


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryCampaignRepository, provides=CampaignRepository)
