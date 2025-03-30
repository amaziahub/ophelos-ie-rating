from operator import is_not

import pytest
import requests
from hamcrest import none, assert_that, equal_to, has_length, is_

from service.schemas.expenditure_schema import ExpenditureSchema
from service.schemas.income_schema import IncomeSchema
from service.schemas.statement_schema import StatementRequest


def test_is_healthy(app):
    assert app.is_healthy()


def test_submit_new_statement(app):
    response = app.submit_statement(build_statement(1))
    is_not(response["statement_id"], none())


def test_retrieve_statement(app):
    response = app.submit_statement(build_statement(1))
    statement_id = response["statement_id"]
    report = app.get_statement(statement_id, 1)
    assert_that(report["id"], equal_to(statement_id))
    assert_that(report["user_id"], equal_to(1))
    assert_that(report["incomes"], has_length(1))
    assert_that(report["incomes"][0]["category"], equal_to("Salary"))
    assert_that(report["incomes"][0]["amount"], equal_to(5000.0))
    assert_that(report["expenditures"], has_length(1))
    assert_that(report["expenditures"][0]["category"], equal_to("Rent"))
    assert_that(report["expenditures"][0]["amount"], equal_to(1500.0))


def test_unable_to_retrieve_statement_of_different_user(app):
    response = app.submit_statement(build_statement(1))
    statement_id = response["statement_id"]

    with pytest.raises(requests.HTTPError) as exc_info:
        app.get_statement(statement_id, 2)

    assert_that(exc_info.value.response.status_code, is_(404))


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
