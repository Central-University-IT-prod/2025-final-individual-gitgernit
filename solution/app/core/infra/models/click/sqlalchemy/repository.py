import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.feed.entities.entities import CampaignClick as DomainClick
from app.core.domain.feed.entities.repositories import ClicksRepository
from app.core.infra.models.click.sqlalchemy.click import Click


class SQLAlchemyClicksRepository(ClicksRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_click(self, click: DomainClick) -> DomainClick:
        async with self._session_factory() as session, session.begin():
            new_click = Click(
                day=click.day,
                cost=click.cost,
                client_id=click.client_id,
                campaign_id=click.campaign_id,
            )

            session.add(new_click)

            await session.flush()
            session.expunge_all()

            return DomainClick(
                id=new_click.id,
                day=new_click.day,
                cost=new_click.cost,
                client_id=new_click.client_id,
                campaign_id=new_click.campaign_id,
            )

    async def get_campaign_clicks(
        self,
        campaign_id: uuid.UUID,
        day: int | None = None,
    ) -> list[DomainClick]:
        async with self._session_factory() as session:
            query = sqlalchemy.select(Click).where(Click.campaign_id == campaign_id)

            if day is not None:
                query = query.where(Click.day == day)

            result = await session.execute(query)
            clicks = result.scalars().all()

            return [
                DomainClick(
                    id=click.id,
                    day=click.day,
                    cost=click.cost,
                    client_id=click.client_id,
                    campaign_id=click.campaign_id,
                )
                for click in clicks
            ]


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(SQLAlchemyClicksRepository, provides=ClicksRepository)
