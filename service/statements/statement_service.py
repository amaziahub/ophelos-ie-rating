from datetime import datetime, timezone
from typing import Type, Any, List

from fastapi import Depends
from sqlalchemy.orm import Session

from service.db import get_db
from service.dependencies import get_user_service
from service.models import StatementDB, IncomeDB, ExpenditureDB
from service.schemas.statement_schema import StatementRequest
from service.users.user_service import UserService

USER_NOT_FOUND = "User not found"
POSITIVE_NUMBER = "Amount must be a positive number"
CATEGORY_CANNOT_BE_EMPTY = "Category cannot be empty"


class EmptyCategoryError(ValueError):
    def __init__(self, message=CATEGORY_CANNOT_BE_EMPTY):
        super().__init__(message)


class NegativeAmountError(ValueError):
    def __init__(self, message=POSITIVE_NUMBER):
        super().__init__(message)


def create_statement_service(
        statement_data: StatementRequest,
        user_service: UserService = Depends(get_user_service),
        db: Session = Depends(get_db)) -> StatementDB:
    user = user_service.get_user_by_id(statement_data.user_id)
    if not user:
        raise LookupError(USER_NOT_FOUND)

    statement = create_statement(db, statement_data)

    incomes = build_records(statement, statement_data.incomes, IncomeDB)
    expenditures = build_records(statement, statement_data.expenditures, ExpenditureDB)

    db.add_all(incomes + expenditures)

    db.commit()
    db.refresh(statement)

    return statement


def build_records(
        statement,
        records_data: list,
        model_class: Type[Any]
) -> List[Any]:
    records = []

    for record in records_data:
        trimmed_category = (
            record.category.strip()) \
            if isinstance(record.category, str) else record.category

        if not trimmed_category:
            raise EmptyCategoryError()

        if record.amount <= 0:
            raise NegativeAmountError()

        records.append(
            model_class(
                category=trimmed_category,
                amount=record.amount,
                statement_id=statement.id
            )
        )

    return records


def create_statement(db, statement_data):
    statement = StatementDB(user_id=statement_data.user_id,
                            report_date=datetime.now(timezone.utc))
    db.add(statement)
    db.flush()
    return statement
