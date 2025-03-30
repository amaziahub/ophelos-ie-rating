from pydantic import BaseModel, Field


class ExpenditureSchema(BaseModel):
    category: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)


class ExpenditureResponse(BaseModel):
    id: int
    category: str
    amount: float

    model_config = {"from_attributes": True}
