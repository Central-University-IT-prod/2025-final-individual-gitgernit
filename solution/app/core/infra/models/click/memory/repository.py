import uuid

import dishka

from app.core.domain.feed.entities.entities import CampaignClick
from app.core.domain.feed.entities.repositories import ClicksRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryClicksRepository(ClicksRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_click(self, click: CampaignClick) -> CampaignClick:
        if click.id is None:
            click.id = uuid.uuid4()
        self._storage.clicks.append(click)
        return click

    async def get_campaign_clicks(
        self,
        campaign_id: uuid.UUID,
        day: int | None = None,
    ) -> list[CampaignClick]:
        return [
            clk
            for clk in self._storage.clicks
            if clk.campaign_id == campaign_id and (day is None or clk.day == day)
        ]


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryClicksRepository, provides=ClicksRepository)
