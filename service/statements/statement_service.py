from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.orm import Session

from service.db import get_db
from service.dependencies import get_user_service
from service.models import StatementDB, IncomeDB, ExpenditureDB
from service.schemas.statement_schema import StatementRequest
from service.users.user_service import UserService


def create_statement_service(
        statement_data: StatementRequest,
        user_service: UserService = Depends(get_user_service),
        db: Session = Depends(get_db)) -> int:
    user = user_service.get_user_by_id(statement_data.user_id)
    if not user:
        raise LookupError("User not found")

    statement = create_statement(db, statement_data)

    incomes = build_income_db_objects(db, statement, statement_data)

    expenditures = build_expenditure_db_objects(statement, statement_data)

    db.add_all(incomes + expenditures)

    db.commit()

    return statement.id


def build_expenditure_db_objects(statement, statement_data):
    expenditures = []
    for expenditure in statement_data.expenditures:
        if not expenditure.category or expenditure.amount <= 0:
            raise ValueError(
                "Invalid expenditure data: "
                "category cannot be empty, amount must be positive")
        expenditures.append(
            ExpenditureDB(category=expenditure.category, amount=expenditure.amount,
                          statement_id=statement.id))
    return expenditures


def build_income_db_objects(db, statement, statement_data):
    incomes = []
    for income in statement_data.incomes:
        if not income.category or income.amount <= 0:
            raise ValueError(
                "Invalid income data: "
                "category cannot be empty, amount must be positive")
        incomes.append(IncomeDB(category=income.category, amount=income.amount,
                                statement_id=statement.id))
    return incomes


def create_statement(db, statement_data):
    statement = StatementDB(user_id=statement_data.user_id,
                            report_date=datetime.now(timezone.utc))
    db.add(statement)
    db.flush()
    return statement
