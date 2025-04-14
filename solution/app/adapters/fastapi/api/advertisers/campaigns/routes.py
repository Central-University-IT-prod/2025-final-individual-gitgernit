import typing
import uuid

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.adapters.fastapi.api.advertisers.campaigns.schemas import (
    CampaignInputSchema,
    CampaignOutputSchema,
    TargetingSchema,
)
from app.core.domain.campaign.service.dto import CampaignDTO, TargetingDTO
from app.core.domain.campaign.service.usecases import (
    AdvertiserNotFoundError,
    CampaignNotFoundError,
    CampaignUsecase,
    InvalidCampaignError,
)
from app.core.infra.yandexgpt.interactors import ResponseDecodingError, UnavailableError

campaigns_router = fastapi.APIRouter(route_class=DishkaRoute)


@campaigns_router.post('', status_code=fastapi.status.HTTP_201_CREATED)
async def create_campaign(
    usecase: FromDishka[CampaignUsecase],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
    campaign: CampaignInputSchema,
) -> CampaignOutputSchema:
    targeting_dto = (
        TargetingDTO(
            gender=campaign.targeting.gender,
            age_from=campaign.targeting.age_from,
            age_to=campaign.targeting.age_to,
            location=campaign.targeting.location,
        )
        if campaign.targeting
        else None
    )
    campaign_dto = CampaignDTO(
        advertiser_id=advertiser_id,
        impressions_limit=campaign.impressions_limit,
        clicks_limit=campaign.clicks_limit,
        cost_per_impression=campaign.cost_per_impression,
        cost_per_click=campaign.cost_per_click,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        image_url=campaign.image_url,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        targeting=targeting_dto,
    )

    try:
        new_campaign = await usecase.create_campaign(campaign_dto)

    except AdvertiserNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such advertiser found.',
        ) from error

    targeting_schema = (
        TargetingSchema(
            gender=new_campaign.targeting.gender,
            age_from=new_campaign.targeting.age_from,
            age_to=new_campaign.targeting.age_to,
            location=new_campaign.targeting.location,
        )
        if new_campaign.targeting
        else None
    )

    return CampaignOutputSchema(
        impressions_limit=new_campaign.impressions_limit,
        clicks_limit=new_campaign.clicks_limit,
        cost_per_impression=new_campaign.cost_per_impression,
        cost_per_click=new_campaign.cost_per_click,
        ad_title=new_campaign.ad_title,
        ad_text=new_campaign.ad_text,
        image_url=new_campaign.image_url,
        start_date=new_campaign.start_date,
        end_date=new_campaign.end_date,
        targeting=targeting_schema,
        campaign_id=new_campaign.id,
        advertiser_id=new_campaign.advertiser_id,
    )


@campaigns_router.get('')
async def get_campaigns(
    usecase: FromDishka[CampaignUsecase],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
    size: int | None = None,
    page: int | None = 0,
) -> list[CampaignOutputSchema]:
    campaigns = await usecase.get_advertiser_campaigns(
        advertiser_id,
        limit=size,
        offset=(size if size else 0) * page,
    )

    return [
        CampaignOutputSchema(
            impressions_limit=campaign_dto.impressions_limit,
            clicks_limit=campaign_dto.clicks_limit,
            cost_per_impression=campaign_dto.cost_per_impression,
            cost_per_click=campaign_dto.cost_per_click,
            ad_title=campaign_dto.ad_title,
            ad_text=campaign_dto.ad_text,
            image_url=campaign_dto.image_url,
            start_date=campaign_dto.start_date,
            end_date=campaign_dto.end_date,
            targeting=TargetingSchema(
                gender=campaign_dto.targeting.gender,
                age_from=campaign_dto.targeting.age_from,
                age_to=campaign_dto.targeting.age_to,
                location=campaign_dto.targeting.location,
            )
            if campaign_dto.targeting
            else None,
            campaign_id=campaign_dto.id,
            advertiser_id=campaign_dto.advertiser_id,
        )
        for campaign_dto in campaigns
    ]


@campaigns_router.get('/{campaignId}')
async def get_campaign(
    usecase: FromDishka[CampaignUsecase],
    campaign_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='campaignId')],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
) -> CampaignOutputSchema:
    campaign_dto = await usecase.get_campaign(campaign_id)

    if campaign_dto is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such campaign.',
        )

    targeting_schema = (
        TargetingSchema(
            gender=campaign_dto.targeting.gender,
            age_from=campaign_dto.targeting.age_from,
            age_to=campaign_dto.targeting.age_to,
            location=campaign_dto.targeting.location,
        )
        if campaign_dto.targeting
        else None
    )

    return CampaignOutputSchema(
        impressions_limit=campaign_dto.impressions_limit,
        clicks_limit=campaign_dto.clicks_limit,
        cost_per_impression=campaign_dto.cost_per_impression,
        cost_per_click=campaign_dto.cost_per_click,
        ad_title=campaign_dto.ad_title,
        ad_text=campaign_dto.ad_text,
        image_url=campaign_dto.image_url,
        start_date=campaign_dto.start_date,
        end_date=campaign_dto.end_date,
        targeting=targeting_schema,
        campaign_id=campaign_dto.id,
        advertiser_id=campaign_dto.advertiser_id,
    )


@campaigns_router.delete(
    '/{campaignId}',
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def delete_campaign(
    usecase: FromDishka[CampaignUsecase],
    campaign_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='campaignId')],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
) -> None:
    try:
        await usecase.delete_campaign(campaign_id, advertiser_id)

    except CampaignNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such campaign found.',
        ) from error


@campaigns_router.put('/{campaignId}')
async def put_campaign(
    usecase: FromDishka[CampaignUsecase],
    campaign_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='campaignId')],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
    campaign: CampaignInputSchema,
) -> CampaignOutputSchema:
    campaign_dto = CampaignDTO(
        advertiser_id=advertiser_id,
        impressions_limit=campaign.impressions_limit,
        clicks_limit=campaign.clicks_limit,
        cost_per_impression=campaign.cost_per_impression,
        cost_per_click=campaign.cost_per_click,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        image_url=campaign.image_url,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        targeting=TargetingDTO(
            gender=campaign.targeting.gender,
            age_from=campaign.targeting.age_from,
            age_to=campaign.targeting.age_to,
            location=campaign.targeting.location,
        )
        if campaign.targeting
        else None,
    )

    try:
        new_campaign_dto = await usecase.patch_campaign(
            campaign_id,
            campaign_dto,
        )

    except InvalidCampaignError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail='Invalid new fields passed.',
        ) from error

    except CampaignNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such campaign found.',
        ) from error

    return CampaignOutputSchema(
        impressions_limit=new_campaign_dto.impressions_limit,
        clicks_limit=new_campaign_dto.clicks_limit,
        cost_per_impression=new_campaign_dto.cost_per_impression,
        cost_per_click=new_campaign_dto.cost_per_click,
        ad_title=new_campaign_dto.ad_title,
        ad_text=new_campaign_dto.ad_text,
        image_url=new_campaign_dto.image_url,
        start_date=new_campaign_dto.start_date,
        end_date=new_campaign_dto.end_date,
        targeting=TargetingSchema(
            gender=new_campaign_dto.targeting.gender,
            age_from=new_campaign_dto.targeting.age_from,
            age_to=new_campaign_dto.targeting.age_to,
            location=new_campaign_dto.targeting.location,
        )
        if new_campaign_dto.targeting
        else None,
        campaign_id=new_campaign_dto.id,
        advertiser_id=new_campaign_dto.advertiser_id,
    )


@campaigns_router.post('/moderate-text')
async def moderate_text(
    usecase: FromDishka[CampaignUsecase],
    data: typing.Annotated[dict[typing.Literal['text'], str], fastapi.Body()],
) -> dict[typing.Literal['valid', 'text'], str | bool]:
    text = data['text']

    if not text:
        msg = 'Blank text passed'
        raise fastapi.exceptions.RequestValidationError(msg)

    try:
        valid = await usecase.moderator.validate_text(text)

    except (ResponseDecodingError, UnavailableError) as error:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error

    return {
        'valid': valid,
        'text': text if valid else '[ MEGAZORDED ]',
    }


@campaigns_router.post('/generate-description')
async def generate_campaign_description(
    usecase: FromDishka[CampaignUsecase],
    data: typing.Annotated[
        dict[typing.Literal['advertiser_name', 'campaign_name'], str],
        fastapi.Body(),
    ],
) -> dict[typing.Literal['result'], str]:
    try:
        generated_description = await usecase.pre_generate_campaign_description(
            data['advertiser_name'],
            data['campaign_name'],
        )

    except (ResponseDecodingError, UnavailableError) as error:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error

    return {
        'result': generated_description,
    }
