import uuid

import pytest

from app.core.domain.advertiser.service.dto import AdvertiserDTO
from app.core.domain.advertiser.service.usecases import AdvertiserUsecase


@pytest.mark.asyncio
class TestAdvertisersUsecase:
    @pytest.fixture(autouse=True)
    def setup(self, advertiser_usecase: AdvertiserUsecase) -> None:
        self.usecase = advertiser_usecase

    async def test_create_advertiser(self) -> None:
        advertiser_dto = AdvertiserDTO(
            id=uuid.uuid4(),
            name='john doe advertisement',
        )

        await self.usecase.create_advertiser(advertiser_dto)
        advertiser = await self.usecase.get_advertiser(advertiser_dto.id)

        assert advertiser is not None
        assert advertiser.name == advertiser_dto.name
