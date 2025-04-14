import uuid

import pydantic


class CampaignImpression(pydantic.BaseModel):
    id: uuid.UUID | None = pydantic.Field(default=None)

    day: int
    cost: float

    campaign_id: uuid.UUID
    client_id: uuid.UUID


class CampaignClick(pydantic.BaseModel):
    id: uuid.UUID | None = pydantic.Field(default=None)

    day: int
    cost: float

    campaign_id: uuid.UUID
    client_id: uuid.UUID
