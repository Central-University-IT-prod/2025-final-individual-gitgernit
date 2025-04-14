import uuid

import dishka

from app.core.domain.client.entities.entities import Client
from app.core.domain.client.entities.repositories import ClientRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryClientRepository(ClientRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def create_client(self, client: Client, *, overwrite: bool = False) -> Client:
        existing_index = next(
            (i for i, c in enumerate(self._storage.clients) if c.id == client.id),
            None,
        )

        if existing_index is not None:
            if overwrite:
                self._storage.clients[existing_index] = client
                return client

            return self._storage.clients[existing_index]

        self._storage.clients.append(client)
        return client

    async def get_client(self, client_id: uuid.UUID) -> Client | None:
        return next(
            (c for c in self._storage.clients if c.id == client_id),
            None,
        )


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryClientRepository, provides=ClientRepository)
