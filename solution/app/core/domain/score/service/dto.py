import uuid

import pydantic


class ScoreDTO(pydantic.BaseModel):
    client_id: uuid.UUID
    advertiser_id: uuid.UUID
    score: int
