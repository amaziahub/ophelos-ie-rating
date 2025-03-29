from pydantic import BaseModel, Field


class IncomeSchema(BaseModel):
    category: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)


class IncomeResponse(BaseModel):
    id: int
    category: str
    amount: float

    class Config:
        from_attributes = True
