import dishka
import sqlalchemy.ext.asyncio


class EngineProvider(dishka.Provider):
    scope = dishka.Scope.APP

    def __init__(self, uri: str) -> None:
        super().__init__()

        self.uri = uri

    @dishka.provide
    async def get_engine(self) -> sqlalchemy.ext.asyncio.engine:
        return sqlalchemy.ext.asyncio.create_async_engine(url=self.uri)


class SessionProvider(dishka.Provider):
    scope = dishka.Scope.REQUEST

    @dishka.provide
    async def get_async_session_factory(
        self,
        engine: sqlalchemy.ext.asyncio.engine,
    ) -> sqlalchemy.ext.asyncio.async_sessionmaker[sqlalchemy.ext.asyncio.AsyncSession]:
        return sqlalchemy.ext.asyncio.async_sessionmaker(bind=engine)
