import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.score.entities.entities import Score as DomainScore
from app.core.domain.score.entities.repositories import ScoreRepository
from app.core.infra.models.score.sqlalchemy.score import Score


class SQLAlchemyScoreRepository(ScoreRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_score(
        self,
        score: DomainScore,
        *,
        overwrite: bool = False,
    ) -> DomainScore:
        async with self._session_factory() as session, session.begin():
            new_score = Score(
                client_id=score.client_id,
                advertiser_id=score.advertiser_id,
                score=score.score,
            )

            if overwrite:
                new_score = await session.merge(new_score)

            session.add(new_score)

            await session.flush()
            session.expunge_all()

            return DomainScore(
                client_id=new_score.client_id,
                advertiser_id=new_score.advertiser_id,
                score=new_score.score,
            )

    async def get_score(
        self,
        user_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> DomainScore | None:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(Score).where(
                Score.client_id == user_id,
                Score.advertiser_id == advertiser_id,
            )
            result = await session.execute(stmt)

            session.expunge_all()

            score = result.scalars().first()

            if score is None:
                return None

            return DomainScore(
                client_id=score.client_id,
                advertiser_id=score.advertiser_id,
                score=score.score,
            )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(SQLAlchemyScoreRepository, provides=ScoreRepository)
