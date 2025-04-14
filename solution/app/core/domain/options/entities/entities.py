import enum

import pydantic


class AvailableOptions(enum.StrEnum):
    DAY = 'DAY'


class Option(pydantic.BaseModel):
    option: AvailableOptions
    value: str | None
