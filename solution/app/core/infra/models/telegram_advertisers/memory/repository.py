import uuid

import dishka

from app.core.infra.models.memory import MemoryStorage
from app.core.infra.models.telegram_advertisers.interface import (
    TelegramAdvertisersRepository,
)
from app.core.infra.models.telegram_advertisers.memory.telegram_advertiser import (
    TelegramAdvertiser,
)


class MemoryTelegramAdvertisersRepository:
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_user(self, telegram_id: str, advertiser_id: uuid.UUID) -> None:
        new_advertiser = TelegramAdvertiser(
            telegram_id=telegram_id,
            advertiser_id=advertiser_id,
        )
        self._storage.telegram_advertisers.append(new_advertiser)

    async def get_advertiser(self, telegram_id: str) -> uuid.UUID | None:
        return next(
            (
                opt.advertiser_id
                for opt in self._storage.telegram_advertisers
                if opt.telegram_id == telegram_id
            ),
            None,
        )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(
    MemoryTelegramAdvertisersRepository,
    provides=TelegramAdvertisersRepository,
)
