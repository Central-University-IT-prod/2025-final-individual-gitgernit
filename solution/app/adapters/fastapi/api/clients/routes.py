import typing
import uuid

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.adapters.fastapi.api.clients.schemas import ClientSchema
from app.core.domain.client.service.dto import ClientDTO
from app.core.domain.client.service.usecases import ClientUsecase

clients_router = fastapi.APIRouter(route_class=DishkaRoute)


@clients_router.post('/bulk', status_code=fastapi.status.HTTP_201_CREATED)
async def bulk_create_clients(
    usecase: FromDishka[ClientUsecase],
    clients: list[ClientSchema],
) -> list[ClientSchema]:
    dtos: list[ClientDTO] = []

    for client in clients:
        dto = ClientDTO(
            id=client.client_id,
            login=client.login,
            age=client.age,
            location=client.location,
            gender=client.gender,
        )

        created_dto = await usecase.create_client(dto, overwrite=True)
        dtos.append(created_dto)

    return [
        ClientSchema(
            client_id=dto.id,
            login=dto.login,
            age=dto.age,
            location=dto.location,
            gender=dto.gender,
        )
        for dto in dtos
    ]


@clients_router.get('/{clientId}')
async def get_client(
    usecase: FromDishka[ClientUsecase],
    client_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='clientId')],
) -> ClientSchema:
    client_dto = await usecase.get_client(client_id=client_id)

    if client_dto is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such client.',
        )

    return ClientSchema(
        client_id=client_dto.id,
        login=client_dto.login,
        age=client_dto.age,
        location=client_dto.location,
        gender=client_dto.gender,
    )
