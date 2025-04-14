import abc
import uuid

from app.core.domain.feed.entities.entities import CampaignClick, CampaignImpression


class ImpressionsRepository(abc.ABC):
    @abc.abstractmethod
    async def create_impression(
        self,
        impression: CampaignImpression,
    ) -> CampaignImpression:
        pass

    @abc.abstractmethod
    async def get_campaign_impressions(
        self,
        campaign_id: uuid.UUID,
        day: int | None = None,
    ) -> list[CampaignImpression]:
        pass


class ClicksRepository(abc.ABC):
    @abc.abstractmethod
    async def create_click(self, click: CampaignClick) -> CampaignClick:
        pass

    @abc.abstractmethod
    async def get_campaign_clicks(
        self,
        campaign_id: uuid.UUID,
        day: int | None = None,
    ) -> list[CampaignClick]:
        pass
