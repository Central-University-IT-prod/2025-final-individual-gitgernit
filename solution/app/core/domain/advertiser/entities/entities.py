import uuid

import pydantic


class Advertiser(pydantic.BaseModel):
    id: uuid.UUID
    name: str
