import abc
import uuid

from app.core.domain.campaign.entities.entities import Campaign
from app.core.domain.client.entities.entities import Gender


class CampaignRepository(abc.ABC):
    @abc.abstractmethod
    async def create_campaign(
        self,
        campaign: Campaign,
        *,
        overwrite: bool = False,
    ) -> Campaign:
        pass

    @abc.abstractmethod
    async def get_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> Campaign | None:
        pass

    @abc.abstractmethod
    async def delete_campaign(
        self,
        campaign_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> None:
        pass

    @abc.abstractmethod
    async def get_advertiser_campaigns(
        self,
        advertiser_id: uuid.UUID,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Campaign]:
        pass

    @abc.abstractmethod
    async def get_targeted_campaigns(
        self,
        age: int,
        location: str,
        gender: Gender,
    ) -> list[Campaign]:
        pass
