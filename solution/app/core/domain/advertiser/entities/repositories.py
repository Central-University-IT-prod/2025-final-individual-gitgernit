import abc
import uuid

from app.core.domain.advertiser.entities.entities import Advertiser


class AdvertiserRepository(abc.ABC):
    @abc.abstractmethod
    async def create_advertiser(
        self,
        advertiser: Advertiser,
        *,
        overwrite: bool = False,
    ) -> Advertiser:
        pass

    @abc.abstractmethod
    async def get_advertiser(self, advertiser_id: uuid.UUID) -> Advertiser | None:
        pass
