import pydantic


class AdvanceSchema(pydantic.BaseModel):
    current_date: int
