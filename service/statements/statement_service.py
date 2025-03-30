from datetime import datetime, timezone
from typing import Type, Any, List, Optional

from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

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


class StatementService:
    def __init__(self, user_service: UserService, db: Session):
        self.user_service = user_service
        self.db = db

    def create_statement(self, statement_data: StatementRequest) -> StatementDB:
        user = self.user_service.get_user_by_id(statement_data.user_id)
        if not user:
            raise LookupError(USER_NOT_FOUND)

        statement = self._create_statement(statement_data)
        incomes = self._build_records(statement, statement_data.incomes, IncomeDB)
        expenditures = self._build_records(statement, statement_data.expenditures,
                                           ExpenditureDB)

        self.db.add_all(incomes + expenditures)
        self.db.commit()
        self.db.refresh(statement)

        return statement

    def get_statement(self, report_id: int, user_id: int) -> StatementDB:
        statement: Optional[StatementDB] = self.db.query(StatementDB).filter(
            StatementDB.id == report_id,
            StatementDB.user_id == user_id
        ).first()

        if statement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Statement not found"
            )

        return statement

    def _create_statement(self, statement_data: StatementRequest) -> StatementDB:
        statement = StatementDB(
            user_id=statement_data.user_id,
            report_date=datetime.now(timezone.utc)
        )
        self.db.add(statement)
        self.db.flush()
        return statement

    @staticmethod
    def _build_records(statement,
                       records_data: list, model_class: Type[Any]) -> List[Any]:
        records = []
        for record in records_data:
            trimmed_category = (
                record.category.strip()
                if isinstance(record.category, str) else record.category
            )

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
