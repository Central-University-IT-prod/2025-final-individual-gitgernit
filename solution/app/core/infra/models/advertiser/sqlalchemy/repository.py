import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.advertiser.entities.entities import Advertiser as DomainAdvertiser
from app.core.domain.advertiser.entities.repositories import AdvertiserRepository
from app.core.infra.models.advertiser.sqlalchemy.advertiser import Advertiser


class SQLAlchemyAdvertiserRepository(AdvertiserRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_advertiser(
        self,
        advertiser: DomainAdvertiser,
        *,
        overwrite: bool = False,
    ) -> DomainAdvertiser:
        async with self._session_factory() as session, session.begin():
            new_advertiser = Advertiser(
                id=advertiser.id,
                name=advertiser.name,
            )

            if overwrite:
                new_advertiser = await session.merge(new_advertiser)

            session.add(new_advertiser)

            await session.flush()
            session.expunge_all()

            return DomainAdvertiser(
                id=new_advertiser.id,
                name=new_advertiser.name,
            )

    async def get_advertiser(self, advertiser_id: uuid.UUID) -> DomainAdvertiser | None:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(Advertiser).where(Advertiser.id == advertiser_id)
            result = await session.execute(stmt)

            session.expunge_all()

            advertiser = result.scalars().first()

            if advertiser is None:
                return None

            return DomainAdvertiser(
                id=advertiser.id,
                name=advertiser.name,
            )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(
    SQLAlchemyAdvertiserRepository,
    provides=AdvertiserRepository,
)
