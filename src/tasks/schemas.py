from datetime import datetime, UTC
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, field_validator, Field


class TaskBaseSchema(BaseModel):
    task_info: str = Field(max_length=256)
    datetime_to_do: datetime


class TaskSchema(TaskBaseSchema):
    id: int


class TaskCreateSchema(TaskBaseSchema):
    @field_validator('datetime_to_do')
    def validate_datetime_to_do(cls, value):
        if value and value.tzinfo is None:
            raise HTTPException(status_code=400, detail='Timezone must be specified.')
        if value and value < datetime.now(UTC):
            raise HTTPException(status_code=400, detail='The date and time must be in the future.')
        return value


class TaskUpdateSchema(TaskCreateSchema):
    task_info: Optional[str] = None
    datetime_to_do: Optional[datetime] = None
