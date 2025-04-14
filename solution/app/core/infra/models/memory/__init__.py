__all__ = ['MemoryStorage']
import dishka
import pydantic

from app.core.domain.advertiser.entities.entities import Advertiser
from app.core.domain.campaign.entities.entities import Campaign
from app.core.domain.client.entities.entities import Client
from app.core.domain.feed.entities.entities import CampaignClick, CampaignImpression
from app.core.domain.options.entities.entities import Option
from app.core.domain.score.entities.entities import Score
from app.core.infra.models.telegram_advertisers.memory.telegram_advertiser import (
    TelegramAdvertiser,
)


class MemoryStorage(pydantic.BaseModel):
    advertisers: list[Advertiser] = pydantic.Field(default=[])
    campaigns: list[Campaign] = pydantic.Field(default=[])
    clients: list[Client] = pydantic.Field(default=[])
    clicks: list[CampaignClick] = pydantic.Field(default=[])
    impressions: list[CampaignImpression] = pydantic.Field(default=[])
    options: list[Option] = pydantic.Field(default=[])
    scores: list[Score] = pydantic.Field(default=[])

    telegram_advertisers: list[TelegramAdvertiser] = pydantic.Field(default=[])


class StorageProvider(dishka.Provider):
    scope = dishka.Scope.APP

    @dishka.provide
    async def get_memory_storage(self) -> MemoryStorage:
        return MemoryStorage()
