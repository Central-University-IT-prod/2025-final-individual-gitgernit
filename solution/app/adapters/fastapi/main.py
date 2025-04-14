import asyncio
import contextlib
import sys

import dishka.integrations.fastapi
import fastapi

import app.adapters.fastapi.api.routes
import app.core.config
import app.core.domain.advertiser.service.usecases
import app.core.domain.campaign.service.usecases
import app.core.domain.client.service.usecases
import app.core.domain.feed.service.usecases
import app.core.domain.options.service.dto
import app.core.domain.options.service.usecases
import app.core.domain.score.service.usecases
import app.core.domain.stats.service.usecases
import app.core.domain.storage.service.usecases

if not app.core.config.config.DEBUG:
    from app.adapters.containers.production import container

else:
    from app.adapters.containers.debug import container

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@contextlib.asynccontextmanager
async def lifespan(fastapi_app: fastapi.FastAPI) -> contextlib.asynccontextmanager:
    async with container() as request_container:
        options_usecase = await request_container.get(
            app.core.domain.options.service.usecases.OptionsUsecase,
        )
        day = await options_usecase.get_option(
            app.core.domain.options.service.dto.AvailableOptionsDTO.DAY,
        )

        if day is None:
            await options_usecase.set_option(
                app.core.domain.options.service.dto.OptionDTO(
                    option=app.core.domain.options.service.dto.AvailableOptionsDTO.DAY,
                    value=str(0),
                ),
            )

    yield
    await fastapi_app.state.dishka_container.close()


main_router = fastapi.APIRouter(
    route_class=dishka.integrations.fastapi.DishkaRoute,
)

fastapi_app = fastapi.FastAPI(lifespan=lifespan)

fastapi_app.include_router(main_router)
fastapi_app.include_router(app.adapters.fastapi.api.routes.api_router)

dishka.integrations.fastapi.setup_dishka(container, fastapi_app)
