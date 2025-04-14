import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.feed.entities.entities import CampaignImpression
from app.core.domain.feed.entities.repositories import ImpressionsRepository
from app.core.infra.models.impression.sqlalchemy.impression import Impression


class SQLAlchemyImpressionsRepository(ImpressionsRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_impression(
        self,
        impression: CampaignImpression,
    ) -> CampaignImpression:
        async with self._session_factory() as session, session.begin():
            new_impression = Impression(
                day=impression.day,
                cost=impression.cost,
                client_id=impression.client_id,
                campaign_id=impression.campaign_id,
            )

            session.add(new_impression)

            await session.flush()
            session.expunge_all()

            return CampaignImpression(
                id=new_impression.id,
                day=new_impression.day,
                cost=new_impression.cost,
                client_id=new_impression.client_id,
                campaign_id=new_impression.campaign_id,
            )

    async def get_campaign_impressions(
        self,
        campaign_id: uuid.UUID,
        day: int | None = None,
    ) -> list[CampaignImpression]:
        async with self._session_factory() as session:
            query = sqlalchemy.select(Impression).where(
                Impression.campaign_id == campaign_id,
            )

            if day is not None:
                query = query.where(Impression.day == day)

            result = await session.execute(query)
            impressions = result.scalars().all()

            return [
                CampaignImpression(
                    id=impression.id,
                    day=impression.day,
                    cost=impression.cost,
                    client_id=impression.client_id,
                    campaign_id=impression.campaign_id,
                )
                for impression in impressions
            ]


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(
    SQLAlchemyImpressionsRepository,
    provides=ImpressionsRepository,
)
