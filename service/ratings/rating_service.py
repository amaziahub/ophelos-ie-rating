from sqlalchemy.orm import Session

from service.schemas.rating_schema import RatingResponse
from service.statements.statement_service import StatementService


class RatingService:
    def __init__(self, db: Session, statement_service: StatementService):
        self.db = db
        self.statement_service = statement_service

    def calculate_ie_rating(self, report_id: int, user_id: int) -> RatingResponse:
        statement = self.statement_service.get_statement(report_id, user_id)

        total_income = sum(income.amount for income in statement.incomes)
        total_expenditure = sum(exp.amount for exp in statement.expenditures)
        disposable_income = self.calculate_disposable_income(total_expenditure,
                                                             total_income)

        ratio = total_expenditure / total_income if total_income > 0 else 1.0

        grade = calculate_grade(ratio)

        return RatingResponse(
            total_income=total_income,
            total_expenditure=total_expenditure,
            disposable_income=disposable_income,
            ratio=ratio,
            grade=grade
        )

    @staticmethod
    def calculate_disposable_income(total_expenditure, total_income):
        disposable_income = total_income - total_expenditure
        return disposable_income


def calculate_grade(ratio: float) -> str:
    if ratio < 0.1:
        return "A"
    elif ratio <= 0.3:
        return "B"
    elif ratio <= 0.5:
        return "C"
    else:
        return "D"
