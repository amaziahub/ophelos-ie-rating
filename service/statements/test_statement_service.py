from datetime import datetime, timezone, timedelta

import pytest
from hamcrest import assert_that, equal_to, has_length

from service.models import UserDB, StatementDB
from service.schemas.expenditure_schema import ExpenditureSchema
from service.schemas.income_schema import IncomeSchema
from service.schemas.statement_schema import StatementRequest
from service.statements.statement_service import StatementService, USER_NOT_FOUND, \
    NegativeAmountError, POSITIVE_NUMBER, EmptyCategoryError, \
    CATEGORY_CANNOT_BE_EMPTY, StatementNotFoundError, STATEMENT_NOT_FOUND, \
    UserNotFoundError
from service.users.user_service import UserService
from service.users.utils import hash_password

INVALID_USER_ID = 999
VALID_USER_ID = 1


@pytest.fixture
def user_service(db):
    user = UserDB(username="steve", password=hash_password("minecraft"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserService(db)


@pytest.fixture
def statement_service(user_service, db):
    return StatementService(user_service=user_service, db=db)


@pytest.fixture
def create_statements(db):
    now = datetime.now(timezone.utc)
    statements = [
        StatementDB(user_id=1, report_date=now - timedelta(days=10)),
        StatementDB(user_id=1, report_date=now - timedelta(days=5)),
        StatementDB(user_id=1, report_date=now)
    ]

    db.add_all(statements)
    db.commit()
    return statements


def test_get_statements_in_period_success(statement_service, create_statements):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=7)
    end_date = now

    result = statement_service.get_statements_in_period(
        user_id=1,
        start_date=start_date,
        end_date=end_date
    )

    assert_that(result, has_length(2))


def test_get_statements_in_period_no_results(statement_service):
    start_date = datetime.now(timezone.utc) - timedelta(days=30)
    end_date = datetime.now(timezone.utc) - timedelta(days=25)

    with pytest.raises(StatementNotFoundError):
        statement_service.get_statements_in_period(
            user_id=1,
            start_date=start_date,
            end_date=end_date
        )


def test_get_statements_in_period_user_not_found(statement_service):
    with pytest.raises(UserNotFoundError):
        statement_service.get_statements_in_period(
            user_id=9999,
            start_date=datetime.now(timezone.utc) - timedelta(days=10),
            end_date=datetime.now(timezone.utc)
        )


def test_get_statements_in_period_only_start_date(statement_service, create_statements):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=6)

    result = statement_service.get_statements_in_period(
        user_id=1,
        start_date=start_date,
        end_date=None
    )

    assert_that(result, has_length(2))


def test_get_statements_in_period_only_end_date(statement_service, create_statements):
    now = datetime.now(timezone.utc)
    end_date = now - timedelta(days=7)

    result = statement_service.get_statements_in_period(
        user_id=1,
        start_date=None,
        end_date=end_date
    )

    assert_that(result, has_length(1))


def test_create_statement_non_existent_user(db, statement_service):
    statement_data = build_statement(INVALID_USER_ID)

    with pytest.raises(UserNotFoundError) as exc_info:
        statement_service.create_statement(statement_data)

    assert_that(str(exc_info.value), equal_to(USER_NOT_FOUND))


def test_create_statement(db, statement_service):
    statement_data = build_statement(VALID_USER_ID)
    statement = statement_service.create_statement(statement_data)

    assert_that(statement.user_id, equal_to(VALID_USER_ID))
    assert_that(statement.report_date.date(),
                equal_to(datetime.now(timezone.utc).date()))


def test_raise_exception_given_negative_amount(db, statement_service):
    statement_data = build_statement(VALID_USER_ID)
    statement_data.incomes[0].amount = -10

    with pytest.raises(NegativeAmountError) as exc_info:
        statement_service.create_statement(statement_data)

    assert_that(str(exc_info.value), equal_to(POSITIVE_NUMBER))


def test_raise_exception_given_empty_category(db, statement_service):
    statement_data = build_statement(VALID_USER_ID)
    statement_data.incomes[0].category = ""

    with pytest.raises(EmptyCategoryError) as exc_info:
        statement_service.create_statement(statement_data)

    assert_that(str(exc_info.value), equal_to(CATEGORY_CANNOT_BE_EMPTY))


def test_successfully_retrieve_statement(db, statement_service):
    statement_data = build_statement(VALID_USER_ID)
    statement = statement_service.create_statement(statement_data)

    retrieved_statement = statement_service.get_statement(statement.id,
                                                          statement.user_id)
    assert_that(retrieved_statement.id, equal_to(statement.id))
    assert_that(retrieved_statement.user_id, equal_to(statement.user_id))


def test_statement_not_found_given_non_existing_report_id(statement_service):
    with pytest.raises(StatementNotFoundError) as exc_info:
        statement_service.get_statement(statement_id=9999, user_id=1)

    assert_that(str(exc_info.value), equal_to(STATEMENT_NOT_FOUND))


def test_retrieve_statement_given_invalid_user(statement_service):
    with pytest.raises(UserNotFoundError) as exc_info:
        statement_service.get_statement(statement_id=1, user_id=INVALID_USER_ID)

    assert_that(str(exc_info.value), equal_to(USER_NOT_FOUND))


def test_retrieve_statement_with_wrong_user(db, statement_service):
    statement_data = build_statement(VALID_USER_ID)
    statement = statement_service.create_statement(statement_data)

    other_user = UserDB(username="user2", password=hash_password("password"))
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    with pytest.raises(Exception) as exc_info:
        statement_service.get_statement(statement_id=statement.id,
                                        user_id=other_user.id)

    assert_that(str(exc_info.value), equal_to(STATEMENT_NOT_FOUND))


def build_statement(user_id):
    return StatementRequest(
        user_id=user_id,
        incomes=[
            IncomeSchema(category="Salary", amount=5000.0),
        ],
        expenditures=[
            ExpenditureSchema(category="Rent", amount=1500.0),
        ]
    )
