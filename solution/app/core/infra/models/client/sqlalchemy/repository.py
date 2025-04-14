import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.client.entities.entities import Client as DomainClient
from app.core.domain.client.entities.entities import Gender as DomainGender
from app.core.domain.client.entities.repositories import ClientRepository
from app.core.infra.models.client.sqlalchemy.client import Client


class SQLAlchemyClientRepository(ClientRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_client(
        self,
        client: DomainClient,
        *,
        overwrite: bool = False,
    ) -> DomainClient:
        async with self._session_factory() as session, session.begin():
            new_client = Client(
                id=client.id,
                login=client.login,
                age=client.age,
                location=client.location,
                gender=client.gender,
            )

            if overwrite:
                new_client = await session.merge(new_client)

            session.add(new_client)

            await session.flush()
            session.expunge_all()

            return DomainClient(
                id=new_client.id,
                login=new_client.login,
                age=new_client.age,
                location=new_client.location,
                gender=DomainGender(new_client.gender),
            )

    async def get_client(self, client_id: uuid.UUID) -> DomainClient | None:
        async with self._session_factory() as session:
            stmt = sqlalchemy.select(Client).where(Client.id == client_id)
            result = await session.execute(stmt)

            session.expunge_all()

            client = result.scalars().first()

            if client is None:
                return None

            return DomainClient(
                id=client.id,
                login=client.login,
                age=client.age,
                location=client.location,
                gender=client.gender,
            )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(
    SQLAlchemyClientRepository,
    provides=ClientRepository,
)
