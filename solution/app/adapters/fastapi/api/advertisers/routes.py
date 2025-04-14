import typing
import uuid

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

import app.adapters.fastapi.api.advertisers.campaigns.routes
from app.adapters.fastapi.api.advertisers.schemas import AdvertiserSchema
from app.core.domain.advertiser.service.dto import AdvertiserDTO
from app.core.domain.advertiser.service.usecases import AdvertiserUsecase

advertisers_router = fastapi.APIRouter(
    route_class=DishkaRoute,
)

advertisers_router.include_router(
    app.adapters.fastapi.api.advertisers.campaigns.routes.campaigns_router,
    prefix='/{advertiserId}/campaigns',
)


@advertisers_router.post('/bulk', status_code=fastapi.status.HTTP_201_CREATED)
async def bulk_create_advertisers(
    usecase: FromDishka[AdvertiserUsecase],
    advertisers: list[AdvertiserSchema],
) -> list[AdvertiserSchema]:
    dtos: list[AdvertiserDTO] = []

    for advertiser in advertisers:
        dto = AdvertiserDTO(
            id=advertiser.advertiser_id,
            name=advertiser.name,
        )

        new_dto = await usecase.create_advertiser(dto, overwrite=True)
        dtos.append(new_dto)

    return [
        AdvertiserSchema(
            advertiser_id=dto.id,
            name=dto.name,
        )
        for dto in dtos
    ]


@advertisers_router.get('/{advertiserId}')
async def get_advertiser(
    usecase: FromDishka[AdvertiserUsecase],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
) -> AdvertiserSchema:
    dto = await usecase.get_advertiser(advertiser_id=advertiser_id)

    if dto is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such advertiser.',
        )

    return AdvertiserSchema(
        advertiser_id=dto.id,
        name=dto.name,
    )
