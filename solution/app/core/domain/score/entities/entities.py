import uuid

import pydantic


class Score(pydantic.BaseModel):
    client_id: uuid.UUID
    advertiser_id: uuid.UUID
    score: int
