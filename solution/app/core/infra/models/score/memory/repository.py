import uuid

import dishka

from app.core.domain.score.entities.entities import Score
from app.core.domain.score.entities.repositories import ScoreRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryScoreRepository(ScoreRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_score(self, score: Score, *, overwrite: bool = False) -> Score:
        existing_index = next(
            (
                i
                for i, s in enumerate(self._storage.scores)
                if s.client_id == score.client_id
                and s.advertiser_id == score.advertiser_id
            ),
            None,
        )

        if existing_index is not None:
            if overwrite:
                self._storage.scores[existing_index] = score
                return score
            return self._storage.scores[existing_index]

        self._storage.scores.append(score)
        return score

    async def get_score(
        self,
        user_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> Score | None:
        return next(
            (
                s
                for s in self._storage.scores
                if s.client_id == user_id and s.advertiser_id == advertiser_id
            ),
            None,
        )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryScoreRepository, provides=ScoreRepository)
