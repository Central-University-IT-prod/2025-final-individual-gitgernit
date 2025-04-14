import abc

from app.core.domain.options.entities.entities import AvailableOptions, Option


class OptionsRepository(abc.ABC):
    @abc.abstractmethod
    async def get_option(self, option: AvailableOptions) -> Option | None:
        pass

    @abc.abstractmethod
    async def set_option(self, option: Option) -> None:
        pass
