from datetime import datetime, timezone

import pytest
from hamcrest import assert_that, equal_to
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.db import Base
from service.models import UserDB
from service.schemas.expenditure_schema import ExpenditureSchema
from service.schemas.income_schema import IncomeSchema
from service.schemas.statement_schema import StatementRequest
from service.statements.statement_service import StatementService, USER_NOT_FOUND, \
    NegativeAmountError, POSITIVE_NUMBER, EmptyCategoryError, CATEGORY_CANNOT_BE_EMPTY
from service.users.user_service import UserService
from service.users.utils import hash_password

INVALID_USER_ID = 999
VALID_USER_ID = 1

TEST_DATABASE_URL = "sqlite:///./test_statement_service.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


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


def test_create_statement_non_existent_user(db, statement_service):
    statement_data = build_statement(INVALID_USER_ID)

    with pytest.raises(LookupError) as exc_info:
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
