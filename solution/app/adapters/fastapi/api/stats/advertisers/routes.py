import typing
import uuid

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.adapters.fastapi.api.stats.schemas import CampaignStatsSchema
from app.core.domain.stats.service.usecases import StatsUsecase

advertisers_router = fastapi.APIRouter(route_class=DishkaRoute)


@advertisers_router.get('/{advertiserId}/campaigns')
async def total_advertiser_campaigns_stats(
    usecase: FromDishka[StatsUsecase],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
) -> CampaignStatsSchema:
    stats_dto = await usecase.get_total_advertisers_campaigns_stats(advertiser_id)

    return CampaignStatsSchema(
        impressions_count=stats_dto.impressions_count,
        clicks_count=stats_dto.clicks_count,
        conversion=stats_dto.conversion,
        spent_impressions=stats_dto.spent_impressions,
        spent_clicks=stats_dto.spent_clicks,
        spent_total=stats_dto.spent_total,
    )


@advertisers_router.get('/{advertiserId}/campaigns/daily')
async def daily_advertiser_campaigns_stats(
    usecase: FromDishka[StatsUsecase],
    advertiser_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='advertiserId')],
) -> list[CampaignStatsSchema]:
    daily_stats_dto = await usecase.get_daily_advertiser_campaign_stats(advertiser_id)

    return [
        CampaignStatsSchema(
            impressions_count=stats_dto.impressions_count,
            clicks_count=stats_dto.clicks_count,
            conversion=stats_dto.conversion,
            spent_impressions=stats_dto.spent_impressions,
            spent_clicks=stats_dto.spent_clicks,
            spent_total=stats_dto.spent_total,
        )
        for stats_dto in daily_stats_dto
    ]
