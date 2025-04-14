import uuid

import pydantic


class AdvertiserDTO(pydantic.BaseModel):
    id: uuid.UUID
    name: str
