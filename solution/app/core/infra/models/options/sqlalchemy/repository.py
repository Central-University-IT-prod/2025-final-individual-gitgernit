import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.options.entities.entities import Option as DomainOption
from app.core.domain.options.entities.repositories import OptionsRepository
from app.core.infra.models.options.sqlalchemy.options import AvailableOptions, Options


class SQLAlchemyOptionsRepository(OptionsRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def set_option(self, option: DomainOption) -> None:
        async with self._session_factory() as session, session.begin():
            new_option = Options(
                option=option.option,
                value=option.value,
            )
            new_option = await session.merge(new_option)

            session.add(new_option)

            await session.flush()
            session.expunge_all()

    async def get_option(self, option: AvailableOptions) -> DomainOption | None:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(Options).where(Options.option == option)
            results = await session.execute(stmt)

            session.expunge_all()

            option = results.scalars().first()

            if option is None:
                return None

            return DomainOption(
                option=option.option,
                value=option.value,
            )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(SQLAlchemyOptionsRepository, provides=OptionsRepository)
