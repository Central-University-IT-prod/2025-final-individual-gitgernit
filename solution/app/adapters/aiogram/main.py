import asyncio
import logging
import sys

import aiogram.dispatcher.dispatcher
import dishka.integrations.aiogram

import app.core.config
import app.core.domain.options.service.dto
import app.core.domain.options.service.usecases
from app.adapters.aiogram.campaigns.handlers import campaigns_router
from app.adapters.aiogram.handlers import main_router
from app.adapters.aiogram.menu.handlers import menu_router

if not app.core.config.config.DEBUG:
    from app.adapters.containers.production import container

else:
    from app.adapters.containers.debug import container

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = aiogram.Bot(token=app.core.config.config.TOKEN_TELEGRAM_API)
dp = aiogram.dispatcher.dispatcher.Dispatcher()

dp.include_routers(
    main_router,
    menu_router,
    campaigns_router,
)


async def main() -> None:
    dishka.integrations.aiogram.setup_dishka(container, dp)

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

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
