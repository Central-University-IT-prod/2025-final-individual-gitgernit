import enum

import pydantic


class AvailableOptionsDTO(enum.StrEnum):
    DAY = 'DAY'


class OptionDTO(pydantic.BaseModel):
    option: AvailableOptionsDTO
    value: str | None
