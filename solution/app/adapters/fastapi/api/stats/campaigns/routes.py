import typing
import uuid

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.adapters.fastapi.api.stats.schemas import CampaignStatsSchema
from app.core.domain.stats.service.usecases import StatsUsecase

campaigns_router = fastapi.APIRouter(route_class=DishkaRoute)


@campaigns_router.get('/{campaignId}')
async def get_campaign_stats(
    usecase: FromDishka[StatsUsecase],
    campaign_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='campaignId')],
) -> CampaignStatsSchema:
    stats_dto = await usecase.get_total_campaign_stats(campaign_id)

    return CampaignStatsSchema(
        impressions_count=stats_dto.impressions_count,
        clicks_count=stats_dto.clicks_count,
        conversion=stats_dto.conversion,
        spent_impressions=stats_dto.spent_impressions,
        spent_clicks=stats_dto.spent_clicks,
        spent_total=stats_dto.spent_total,
    )


@campaigns_router.get('/{campaignId}/daily')
async def get_dailyy_campaign_stats(
    usecase: FromDishka[StatsUsecase],
    campaign_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='campaignId')],
) -> list[CampaignStatsSchema]:
    daily_stats_dto = await usecase.get_daily_campaign_stats(campaign_id)

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
