import dishka

from app.core.domain.options.entities.entities import AvailableOptions, Option
from app.core.domain.options.entities.repositories import OptionsRepository
from app.core.infra.models.memory import MemoryStorage


class MemoryOptionsRepository(OptionsRepository):
    def __init__(self, storage: MemoryStorage) -> None:
        self._storage = storage

    async def get_option(self, option: AvailableOptions) -> Option | None:
        return next(
            (opt for opt in self._storage.options if opt.option == option),
            None,
        )

    async def set_option(self, option: Option) -> None:
        existing_index = next(
            (
                i
                for i, opt in enumerate(self._storage.options)
                if opt.option == option.option
            ),
            None,
        )

        if existing_index is not None:
            self._storage.options[existing_index] = option

        else:
            self._storage.options.append(option)


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(MemoryOptionsRepository, provides=OptionsRepository)
