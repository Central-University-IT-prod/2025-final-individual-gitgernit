import enum
import uuid

import pydantic


class Gender(enum.StrEnum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    ALL = 'ALL'


class Targeting(pydantic.BaseModel):
    gender: Gender | None = pydantic.Field(default=None)
    age_from: int | None = pydantic.Field(default=None)
    age_to: int | None = pydantic.Field(default=None)
    location: str | None = pydantic.Field(default=None)


class Campaign(pydantic.BaseModel):
    id: uuid.UUID | None = pydantic.Field(default=None)
    advertiser_id: uuid.UUID

    impressions_limit: int
    clicks_limit: int

    cost_per_impression: float
    cost_per_click: float

    ad_title: str
    ad_text: str
    image_url: pydantic.AnyUrl | None = pydantic.Field(default=None)

    start_date: int
    end_date: int

    targeting: Targeting | None = pydantic.Field(default=None)

    async def started(self, current_day: int) -> bool:
        return current_day >= self.start_date

    async def ended(self, current_day: int) -> bool:
        return current_day > self.end_date
