from operator import is_not

import pytest
import requests
from hamcrest import none, assert_that, equal_to, has_length, is_

from service.db import Base, engine
from service.schemas.expenditure_schema import ExpenditureSchema
from service.schemas.income_schema import IncomeSchema
from service.schemas.statement_schema import StatementRequest
from service.statements.statement_service import USER_NOT_FOUND, STATEMENT_NOT_FOUND
from service.users.user_service import UserService


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


def test_calculate_ie_rating_success(app):
    response = app.submit_statement(build_statement(1))
    statement_id = response["statement_id"]

    rating_response = app.get_rating(statement_id, 1)

    assert_that(rating_response["total_income"], equal_to(5000.0))
    assert_that(rating_response["total_expenditure"], equal_to(1500.0))
    assert_that(rating_response["disposable_income"], equal_to(3500.0))
    assert_that(rating_response["grade"], equal_to("B"))


def test_calculate_ie_rating_user_not_found(app):
    with pytest.raises(requests.HTTPError) as exc_info:
        app.get_rating(1, 999)

    assert_that(exc_info.value.response.status_code, is_(404))
    assert_that(exc_info.value.response.json()["detail"], equal_to(USER_NOT_FOUND))


def test_calculate_ie_rating_statement_not_found(app):
    with pytest.raises(requests.HTTPError) as exc_info:
        app.get_rating(999, 1)
    assert_that(exc_info.value.response.status_code, is_(404))
    assert_that(exc_info.value.response.json()["detail"], equal_to(STATEMENT_NOT_FOUND))


def test_calculate_period_rating(app):
    clean_db()

    app.submit_statement(build_statement(1))
    app.submit_statement(build_statement(1))

    response = app.get_rating_period(1, start_date="2025-01-01", end_date="2025-12-31")

    assert_that(response["total_income"], equal_to(10000.0))
    assert_that(response["total_expenditure"], equal_to(3000.0))
    assert_that(response["grade"], equal_to("B"))


def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    UserService.insert_default_users()


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
