import uuid

import pydantic


class TelegramAdvertiser(pydantic.BaseModel):
    telegram_id: str
    advertiser_id: uuid.UUID
