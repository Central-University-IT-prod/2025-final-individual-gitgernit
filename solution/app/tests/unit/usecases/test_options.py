import pytest

from app.core.domain.options.service.dto import AvailableOptionsDTO, OptionDTO
from app.core.domain.options.service.usecases import OptionsUsecase


@pytest.mark.asyncio
class TestOptionsUsecase:
    @pytest.fixture(autouse=True)
    def setup(self, options_usecase: OptionsUsecase) -> None:
        self.usecase = options_usecase

    async def test_create_option(self) -> None:
        option_dto = OptionDTO(
            option=AvailableOptionsDTO.DAY,
            value='1984',
        )

        await self.usecase.set_option(option_dto)
        option = await self.usecase.get_option(AvailableOptionsDTO.DAY)

        assert option is not None
        assert option.value == '1984'
