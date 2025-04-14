import uuid

import pydantic


class ScoreSchema(pydantic.BaseModel):
    client_id: uuid.UUID
    advertiser_id: uuid.UUID
    score: int


class CampaignOutputSchema(pydantic.BaseModel):
    ad_id: uuid.UUID
    advertiser_id: uuid.UUID

    ad_title: str
    ad_text: str
