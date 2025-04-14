import uuid

import pydantic


class AdvertiserSchema(pydantic.BaseModel):
    advertiser_id: uuid.UUID
    name: str
