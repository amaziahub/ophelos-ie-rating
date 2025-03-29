from pydantic import BaseModel, Field


class Greeter(BaseModel):
    name: str = Field(..., min_length=1)
    greet_msg: str = Field(..., min_length=1)
    user_id: int = Field(..., gt=0)
