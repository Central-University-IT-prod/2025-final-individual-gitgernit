import abc
import uuid

from app.core.domain.client.entities.entities import Client


class ClientRepository(abc.ABC):
    @abc.abstractmethod
    async def create_client(self, client: Client, *, overwrite: bool = False) -> Client:
        pass

    @abc.abstractmethod
    async def get_client(self, client_id: uuid.UUID) -> Client | None:
        pass
