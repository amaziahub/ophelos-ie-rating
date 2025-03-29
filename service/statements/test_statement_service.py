from operator import is_not

import pytest
from hamcrest import assert_that, equal_to, none
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.db import Base
from service.models import UserDB
from service.schemas.expenditure_schema import ExpenditureSchema
from service.schemas.income_schema import IncomeSchema
from service.schemas.statement_schema import StatementRequest
from service.statements.statement_service import create_statement_service
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


def test_create_statement_non_existent_user(db, user_service):
    statement_data = build_statement(INVALID_USER_ID)

    with pytest.raises(LookupError) as exc_info:
        create_statement_service(statement_data, user_service=user_service, db=db)

    assert_that(str(exc_info.value), equal_to("User not found"))


def test_create_statement(db, user_service):
    statement_data = build_statement(VALID_USER_ID)
    statement_id = create_statement_service(statement_data,
                                            user_service=user_service,
                                            db=db)
    is_not(statement_id, none())


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
    return statement_data
