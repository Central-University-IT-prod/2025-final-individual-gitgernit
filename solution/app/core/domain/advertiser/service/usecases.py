import uuid

import dishka

from app.core.domain.advertiser.entities.entities import Advertiser
from app.core.domain.advertiser.entities.repositories import AdvertiserRepository
from app.core.domain.advertiser.service.dto import AdvertiserDTO


class AdvertiserUsecase:
    def __init__(self, advertiser_repository: AdvertiserRepository) -> None:
        self.advertiser_repository = advertiser_repository

    async def create_advertiser(
        self,
        dto: AdvertiserDTO,
        *,
        overwrite: bool = False,
    ) -> AdvertiserDTO:
        advertiser = Advertiser(
            id=dto.id,
            name=dto.name,
        )
        new_advertiser = await self.advertiser_repository.create_advertiser(
            advertiser,
            overwrite=overwrite,
        )

        return AdvertiserDTO(
            id=new_advertiser.id,
            name=new_advertiser.name,
        )

    async def get_advertiser(self, advertiser_id: uuid.UUID) -> AdvertiserDTO | None:
        advertiser = await self.advertiser_repository.get_advertiser(
            advertiser_id=advertiser_id,
        )

        if advertiser is None:
            return None

        return AdvertiserDTO(
            id=advertiser.id,
            name=advertiser.name,
        )


usecase_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
usecase_provider.provide(AdvertiserUsecase)
