import pytest
from hamcrest import assert_that, equal_to
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.db import Base
from service.ratings.rating_service import RatingService
from service.statements.statement_service import StatementService, \
    StatementNotFoundError
from service.models import UserDB, StatementDB, IncomeDB, ExpenditureDB
from service.users.user_service import UserService
from service.users.utils import hash_password

TEST_DATABASE_URL = "sqlite:///./test_rating_service.db"
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
    return UserService(db)


@pytest.fixture
def statement_service(db, user_service):
    return StatementService(user_service=user_service, db=db)


@pytest.fixture
def rating_service(statement_service, db):
    return RatingService(db=db, statement_service=statement_service)


@pytest.fixture
def create_user(user_service):
    user_data = UserDB(username="test_user", password=hash_password("password"))
    user_service.db.add(user_data)
    user_service.db.commit()
    user_service.db.refresh(user_data)
    return user_data


@pytest.fixture
def create_statement(db, create_user):
    statement = StatementDB(user_id=create_user.id)
    db.add(statement)
    db.commit()
    db.refresh(statement)

    db.add_all([
        IncomeDB(category="Salary", amount=5000.0, statement_id=statement.id),
        IncomeDB(category="Bonus", amount=2000.0, statement_id=statement.id)
    ])

    db.add_all([
        ExpenditureDB(category="Rent", amount=1500.0, statement_id=statement.id),
        ExpenditureDB(category="Food", amount=500.0, statement_id=statement.id)
    ])

    db.commit()
    return statement


def test_calculate_ie_rating_success(rating_service, create_statement, create_user):
    result = rating_service.calculate_ie_rating(report_id=create_statement.id,
                                                user_id=create_user.id)

    assert_that(result.total_income, equal_to(7000.0))  # 5000 + 2000
    assert_that(result.total_expenditure, equal_to(2000.0))  # 1500 + 500
    assert_that(result.disposable_income, equal_to(5000.0))  # 7000 - 2000
    assert_that(result.grade, equal_to("B"))  # Ratio is between 10% - 30%


def test_calculate_ie_rating_no_income(rating_service, create_statement, db):
    db.query(IncomeDB).delete()
    db.commit()

    result = rating_service.calculate_ie_rating(report_id=create_statement.id,
                                                user_id=create_statement.user_id)

    assert_that(result.total_income, equal_to(0.0))
    assert_that(result.total_expenditure, equal_to(2000.0))
    assert_that(result.disposable_income, equal_to(-2000.0))
    assert_that(result.grade, equal_to("D"))


def test_calculate_ie_rating_no_expenditure(rating_service, create_statement, db):
    db.query(ExpenditureDB).delete()
    db.commit()

    result = rating_service.calculate_ie_rating(report_id=create_statement.id,
                                                user_id=create_statement.user_id)

    assert_that(result.total_income, equal_to(7000.0))
    assert_that(result.total_expenditure, equal_to(0.0))
    assert_that(result.disposable_income, equal_to(7000.0))
    assert_that(result.grade, equal_to("A"))


def test_calculate_ie_rating_no_income_no_expenditure(rating_service, create_statement,
                                                      db):
    db.query(IncomeDB).delete()
    db.query(ExpenditureDB).delete()
    db.commit()

    result = rating_service.calculate_ie_rating(report_id=create_statement.id,
                                                user_id=create_statement.user_id)

    assert_that(result.total_income, equal_to(0.0))
    assert_that(result.total_expenditure, equal_to(0.0))
    assert_that(result.disposable_income, equal_to(0.0))
    assert_that(result.grade, equal_to("D"))


def test_calculate_ie_rating_statement_not_found(create_user, rating_service):
    with pytest.raises(StatementNotFoundError):
        rating_service.calculate_ie_rating(report_id=9999, user_id=1)
