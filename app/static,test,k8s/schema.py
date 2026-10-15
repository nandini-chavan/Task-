from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    task: str = Field(..., min_length=1, max_length=100)


class TaskUpdate(BaseModel):
    completed: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = ConfigDict(from_attributes=True, extra="forbid")