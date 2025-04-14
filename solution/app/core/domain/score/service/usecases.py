import uuid

import dishka

from app.core.domain.advertiser.entities.repositories import AdvertiserRepository
from app.core.domain.client.entities.repositories import ClientRepository
from app.core.domain.score.entities.entities import Score
from app.core.domain.score.entities.repositories import ScoreRepository
from app.core.domain.score.service.dto import ScoreDTO


class ClientNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__('No such client found.')


class AdvertiserNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__('No such advertiser found.')


class ScoreUsecase:
    def __init__(
        self,
        score_repository: ScoreRepository,
        client_repository: ClientRepository,
        advertiser_repository: AdvertiserRepository,
    ) -> None:
        self.score_repository = score_repository
        self.client_repository = client_repository
        self.advertiser_repository = advertiser_repository

    async def create_score(self, dto: ScoreDTO, *, overwrite: bool = False) -> ScoreDTO:
        if await self.client_repository.get_client(dto.client_id) is None:
            raise ClientNotFoundError

        if await self.advertiser_repository.get_advertiser(dto.advertiser_id) is None:
            raise AdvertiserNotFoundError

        score = Score(
            client_id=dto.client_id,
            advertiser_id=dto.advertiser_id,
            score=dto.score,
        )
        new_score = await self.score_repository.create_score(score, overwrite=overwrite)

        return ScoreDTO(
            client_id=new_score.client_id,
            advertiser_id=new_score.advertiser_id,
            score=new_score.score,
        )

    async def get_score(
        self,
        user_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> ScoreDTO | None:
        score = await self.score_repository.get_score(user_id, advertiser_id)

        if score is None:
            return None

        return ScoreDTO(
            client_id=score.client_id,
            advertiser_id=score.advertiser_id,
            score=score.score,
        )


usecase_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
usecase_provider.provide(ScoreUsecase)
