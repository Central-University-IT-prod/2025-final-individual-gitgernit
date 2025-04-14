import pytest
import uuid

from app.core.domain.score.service.dto import ScoreDTO
from app.core.domain.score.service.usecases import ScoreUsecase
from app.core.domain.advertiser.service.dto import AdvertiserDTO
from app.core.domain.client.service.dto import ClientDTO, Gender
from app.core.domain.advertiser.service.usecases import AdvertiserUsecase
from app.core.domain.client.service.usecases import ClientUsecase


@pytest.mark.asyncio
class TestScoreUsecase:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        score_usecase: ScoreUsecase,
        advertiser_usecase: AdvertiserUsecase,
        client_usecase: ClientUsecase,
    ) -> None:
        self.score_usecase = score_usecase
        self.advertiser_usecase = advertiser_usecase
        self.client_usecase = client_usecase

    async def test_set_and_get_score(self) -> None:
        client_id = uuid.uuid4()
        advertiser_id = uuid.uuid4()

        client_dto = ClientDTO(
            id=client_id,
            login="jane doe",
            age=30,
            location="гиперборея",
            gender=Gender.MALE,
        )
        await self.client_usecase.create_client(client_dto)

        advertiser_dto = AdvertiserDTO(id=advertiser_id, name="john doe advertisement inc")
        await self.advertiser_usecase.create_advertiser(advertiser_dto)

        score_dto = ScoreDTO(client_id=client_id, advertiser_id=advertiser_id, score=85)
        await self.score_usecase.create_score(score_dto)

        score = await self.score_usecase.get_score(client_id, advertiser_id)

        assert score is not None
        assert score.score == 85
