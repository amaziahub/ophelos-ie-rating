from datetime import datetime
from typing import List

from pydantic import BaseModel

from service.schemas.expenditure_schema import ExpenditureSchema, ExpenditureResponse
from service.schemas.income_schema import IncomeSchema, IncomeResponse


class StatementRequest(BaseModel):
    user_id: int
    incomes: List[IncomeSchema] = []
    expenditures: List[ExpenditureSchema] = []


class StatementCreateResponse(BaseModel):
    statement_id: int


class StatementResponse(BaseModel):
    id: int
    user_id: int
    report_date: datetime
    incomes: List[IncomeResponse]
    expenditures: List[ExpenditureResponse]

    model_config = {"from_attributes": True}
