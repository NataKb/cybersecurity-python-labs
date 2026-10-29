from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StatusEnum(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=40)

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Назва категорії не може бути порожньою")
        return value


class CategoryRead(CategoryCreate):
    id: int = Field(gt=0)


class RecordCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    code: str = Field(min_length=3, max_length=40)
    title: str = Field(min_length=3, max_length=120)
    category_id: int = Field(gt=0)
    value: float = Field(ge=0, allow_inf_nan=False)
    status: StatusEnum

    @field_validator("code", "title")
    @classmethod
    def check_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Поле не може бути порожнім")
        return value


class RecordReplace(RecordCreate):
    pass


class RecordRead(BaseModel):
    id: int
    code: str
    title: str
    category_id: int
    category_name: str
    value: float
    status: StatusEnum
