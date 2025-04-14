import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.infra.models.telegram_advertisers.interface import (
    TelegramAdvertisersRepository,
)
from app.core.infra.models.telegram_advertisers.sqlalchemy.telegram_advertiser import (
    TelegramAdvertiser,
)


class SQLAlchemyTelegramAdvertisersRepository:
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_user(self, telegram_id: str, advertiser_id: uuid.UUID) -> None:
        async with self._session_factory() as session, session.begin():
            new_advertiser = TelegramAdvertiser(
                telegram_id=telegram_id,
                advertiser_id=advertiser_id,
            )

            session.add(new_advertiser)

            await session.flush()
            session.expunge_all()

    async def get_advertiser(self, telegram_id: str) -> uuid.UUID | None:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(TelegramAdvertiser).where(
                TelegramAdvertiser.telegram_id == telegram_id,
            )
            results = await session.execute(stmt)

            session.expunge_all()

            option = results.scalars().first()

            if option is None:
                return None

            return option.advertiser_id


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(
    SQLAlchemyTelegramAdvertisersRepository,
    provides=TelegramAdvertisersRepository,
)
