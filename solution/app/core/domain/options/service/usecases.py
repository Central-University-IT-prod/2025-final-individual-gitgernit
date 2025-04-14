import dishka

from app.core.domain.options.entities.entities import AvailableOptions, Option
from app.core.domain.options.entities.repositories import OptionsRepository
from app.core.domain.options.service.dto import AvailableOptionsDTO, OptionDTO


class InvalidDayError(Exception):
    def __init__(self) -> None:
        super().__init__('Invalid day passed.')


class OptionsUsecase:
    def __init__(self, options_repository: OptionsRepository) -> None:
        self.options_repository = options_repository

    async def set_option(self, dto: OptionDTO) -> None:
        enum_option = AvailableOptions(dto.option)
        option = Option(
            option=enum_option,
            value=dto.value,
        )

        match option.option:
            case AvailableOptions.DAY:
                new_day = int(dto.value)
                current_day_option = await self.options_repository.get_option(
                    AvailableOptions.DAY,
                )

                if current_day_option is not None:
                    current_day = int(current_day_option.value)

                    if new_day < current_day:
                        raise InvalidDayError

        await self.options_repository.set_option(option)

    async def get_option(self, option: AvailableOptionsDTO) -> OptionDTO | None:
        domain_option_enum = AvailableOptions(option)
        domain_option = await self.options_repository.get_option(domain_option_enum)

        if domain_option is None:
            return None

        return OptionDTO(
            option=AvailableOptionsDTO(domain_option.option),
            value=domain_option.value,
        )

    async def increment_option(self, option: AvailableOptionsDTO, delta: int) -> None:
        domain_option_enum = AvailableOptions(option)
        domain_option = await self.options_repository.get_option(domain_option_enum)

        domain_option.value += delta
        await self.options_repository.set_option(domain_option)


usecase_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
usecase_provider.provide(OptionsUsecase)
