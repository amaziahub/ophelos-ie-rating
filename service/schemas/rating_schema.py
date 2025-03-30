from pydantic import BaseModel


class RatingResponse(BaseModel):
    total_income: float
    total_expenditure: float
    disposable_income: float
    ratio: float
    grade: str

    model_config = {"from_attributes": True}
