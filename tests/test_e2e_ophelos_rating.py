from operator import is_not

from hamcrest import none

from service.schemas.expenditure_schema import ExpenditureSchema
from service.schemas.income_schema import IncomeSchema
from service.schemas.statement_schema import StatementRequest


def test_is_healthy(app):
    assert app.is_healthy()


def test_submit_new_statement(app):
    response = app.submit_statement(build_statement(1))
    is_not(response["statement_id"], none())


def build_statement(user_id):
    statement_data = StatementRequest(
        user_id=user_id,
        incomes=[
            IncomeSchema(category="Salary", amount=5000.0),
        ],
        expenditures=[
            ExpenditureSchema(category="Rent", amount=1500.0),
        ]
    )

    return statement_data.model_dump_json()
