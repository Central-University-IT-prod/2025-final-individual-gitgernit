import enum
import uuid

import pydantic


class Gender(enum.StrEnum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'


class ClientDTO(pydantic.BaseModel):
    id: uuid.UUID
    login: str
    age: int
    location: str
    gender: Gender
