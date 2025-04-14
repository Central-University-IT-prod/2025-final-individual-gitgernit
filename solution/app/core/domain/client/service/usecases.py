import uuid

import dishka

from app.core.domain.client.entities.entities import Client
from app.core.domain.client.entities.repositories import ClientRepository
from app.core.domain.client.service.dto import ClientDTO


class ClientUsecase:
    def __init__(self, client_repository: ClientRepository) -> None:
        self.repository = client_repository

    async def create_client(
        self,
        dto: ClientDTO,
        *,
        overwrite: bool = False,
    ) -> ClientDTO:
        client = Client(**dto.model_dump())
        client = await self.repository.create_client(client, overwrite=overwrite)

        return ClientDTO(
            id=client.id,
            login=client.login,
            age=client.age,
            location=client.location,
            gender=client.gender,
        )

    async def get_client(self, client_id: uuid.UUID) -> ClientDTO | None:
        client = await self.repository.get_client(client_id)

        if client is None:
            return None

        return ClientDTO(
            id=client.id,
            login=client.login,
            age=client.age,
            location=client.location,
            gender=client.gender,
        )


usecase_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
usecase_provider.provide(ClientUsecase)
