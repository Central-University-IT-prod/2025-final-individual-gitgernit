import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.adapters.fastapi.api.time.schemas import AdvanceSchema
from app.core.domain.options.service.dto import AvailableOptionsDTO, OptionDTO
from app.core.domain.options.service.usecases import InvalidDayError, OptionsUsecase

time_router = fastapi.APIRouter(route_class=DishkaRoute)


@time_router.post('/advance')
async def advance_day(
    usecase: FromDishka[OptionsUsecase],
    advance_schema: AdvanceSchema | None = None,
) -> AdvanceSchema:
    if advance_schema:
        dto = OptionDTO(
            option=AvailableOptionsDTO.DAY,
            value=str(advance_schema.current_date),
        )

        try:
            await usecase.set_option(dto)

        except InvalidDayError as error:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail='Invalid date passed.',
            ) from error

    else:
        await usecase.increment_option(AvailableOptionsDTO.DAY, 1)

    return advance_schema
