import abc
import uuid

from app.core.domain.score.entities.entities import Score


class ScoreRepository(abc.ABC):
    @abc.abstractmethod
    async def create_score(self, score: Score, *, overwrite: bool = False) -> Score:
        pass

    @abc.abstractmethod
    async def get_score(
        self,
        user_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> Score | None:
        pass
