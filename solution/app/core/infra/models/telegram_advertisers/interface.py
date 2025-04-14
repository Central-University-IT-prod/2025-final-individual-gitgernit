import abc
import uuid


class TelegramAdvertisersRepository(abc.ABC):
    @abc.abstractmethod
    async def create_user(self, telegram_id: str, advertiser_id: uuid.UUID) -> None:
        pass

    @abc.abstractmethod
    async def get_advertiser(self, telegram_id: str) -> uuid.UUID | None:
        pass
