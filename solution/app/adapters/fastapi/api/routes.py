import asyncio
import typing
import uuid

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

import app.adapters.fastapi.api.advertisers.routes
import app.adapters.fastapi.api.clients.routes
import app.adapters.fastapi.api.stats.routes
import app.adapters.fastapi.api.storage.routes
import app.adapters.fastapi.api.time.routes
from app.adapters.fastapi.api.schemas import CampaignOutputSchema, ScoreSchema
from app.core.domain.feed.service.usecases import (
    CampaignInactiveError as FeedCampaignInactiveError,
)
from app.core.domain.feed.service.usecases import (
    CampaignNotFoundError as FeedCampaignNotFoundError,
)
from app.core.domain.feed.service.usecases import (
    ClientNotFoundError as FeedClientNotFoundError,
)
from app.core.domain.feed.service.usecases import (
    FeedUsecase,
)
from app.core.domain.feed.service.usecases import NotAllowedError as FeedNotAllowedError
from app.core.domain.score.service.dto import ScoreDTO
from app.core.domain.score.service.usecases import (
    AdvertiserNotFoundError as ScoreAdvertiserNotFoundError,
)
from app.core.domain.score.service.usecases import (
    ClientNotFoundError as ScoreClientNotFoundError,
)
from app.core.domain.score.service.usecases import (
    ScoreUsecase,
)

lock = asyncio.Lock()

api_router = fastapi.APIRouter(
    route_class=DishkaRoute,
)

api_router.include_router(
    app.adapters.fastapi.api.clients.routes.clients_router,
    prefix='/clients',
)
api_router.include_router(
    app.adapters.fastapi.api.advertisers.routes.advertisers_router,
    prefix='/advertisers',
)
api_router.include_router(
    app.adapters.fastapi.api.time.routes.time_router,
    prefix='/time',
)
api_router.include_router(
    app.adapters.fastapi.api.stats.routes.stats_router,
    prefix='/stats',
)
api_router.include_router(
    app.adapters.fastapi.api.storage.routes.storage_router,
    prefix='/storage',
)


@api_router.get('/ping')
async def pong() -> str:
    return 'pong'


@api_router.post('/ml-scores')
async def create_score(
    usecase: FromDishka[ScoreUsecase],
    score: ScoreSchema,
) -> None:
    dto = ScoreDTO(
        client_id=score.client_id,
        advertiser_id=score.advertiser_id,
        score=score.score,
    )

    try:
        await usecase.create_score(dto, overwrite=True)

    except ScoreClientNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such client.',
        ) from error

    except ScoreAdvertiserNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='No such advertiser.',
        ) from error


@api_router.get('/ads')
async def get_campaign(
    usecase: FromDishka[FeedUsecase],
    client_id: uuid.UUID,
) -> CampaignOutputSchema:
    async with lock:
        try:
            best_campaign_dto = await usecase.get_best_campaign(client_id)

        except FeedClientNotFoundError as error:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail='Client not found.',
            ) from error

        except FeedCampaignNotFoundError as error:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail='No campaign found.',
            ) from error

        return CampaignOutputSchema(
            ad_id=best_campaign_dto.id,
            advertiser_id=best_campaign_dto.advertiser_id,
            ad_title=best_campaign_dto.ad_title,
            ad_text=best_campaign_dto.ad_text,
        )


@api_router.post('/ads/{adId}/click', status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def click_campaign(
    usecase: FromDishka[FeedUsecase],
    campaign_id: typing.Annotated[uuid.UUID, fastapi.Path(alias='adId')],
    client_id: typing.Annotated[uuid.UUID, fastapi.Body(embed=True)],
) -> None:
    async with lock:
        try:
            await usecase.click_campaign(client_id, campaign_id)

        except FeedClientNotFoundError as error:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail='Client not found.',
            ) from error

        except FeedCampaignNotFoundError as error:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail='No campaign found.',
            ) from error

        except FeedCampaignInactiveError as error:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail='Campaign is inactive (by any means).',
            ) from error

        except FeedNotAllowedError:
            # raise fastapi.HTTPException(
            #     status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            #     detail='Click forbidden.',
            # ) from error
            pass
