from datetime import datetime, timezone, timedelta

import pytest
from hamcrest import assert_that, equal_to

from service.models import UserDB, StatementDB, IncomeDB, ExpenditureDB
from service.ratings.rating_service import RatingService
from service.schemas.rating_schema import RatingResponse
from service.statements.statement_service import StatementService, \
    StatementNotFoundError, UserNotFoundError
from service.users.user_service import UserService
from service.users.utils import hash_password


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


@pytest.fixture
def create_statements_for_period(db, create_user):
    now = datetime.now(timezone.utc)
    statements = [
        StatementDB(user_id=create_user.id, report_date=now - timedelta(days=10)),
        StatementDB(user_id=create_user.id, report_date=now - timedelta(days=5)),
        StatementDB(user_id=create_user.id, report_date=now)
    ]

    db.add_all(statements)
    db.commit()
    db.refresh(statements[0])
    db.refresh(statements[1])
    db.refresh(statements[2])

    for statement in statements:
        incomes = [
            IncomeDB(category="Salary", amount=5000.0, statement_id=statement.id),
            IncomeDB(category="Freelance", amount=1500.0, statement_id=statement.id)
        ]

        expenditures = [
            ExpenditureDB(category="Rent", amount=1200.0, statement_id=statement.id),
            ExpenditureDB(category="Groceries", amount=300.0, statement_id=statement.id)
        ]

        db.add_all(incomes + expenditures)
        db.commit()

    return statements


def create_statement_with_data(db, user_id, incomes, expenditures):
    statement = StatementDB(user_id=user_id)
    db.add(statement)
    db.commit()
    db.refresh(statement)

    db.add_all([
        IncomeDB(category=income['category'], amount=income['amount'],
                 statement_id=statement.id)
        for income in incomes
    ])

    db.add_all([
        ExpenditureDB(category=expenditure['category'], amount=expenditure['amount'],
                      statement_id=statement.id)
        for expenditure in expenditures
    ])

    db.commit()
    return statement


@pytest.mark.parametrize("total_income, total_expenditure, expected_grade", [
    (10000.0, 4000.0, "C"),
    (10000.0, 1000.0, "A"),
    (10000.0, 2000.0, "B"),
    (10000.0, 6000.0, "D")
])
def test_calculate_ie_rating_all_grades(rating_service, create_user, db, total_income,
                                        total_expenditure, expected_grade):
    statement = create_statement_with_data(
        db,
        create_user.id,
        incomes=[{"category": "Job", "amount": total_income}],
        expenditures=[
            {"category": "Rent", "amount": total_expenditure}
        ]
    )

    result = rating_service.calculate_ie_rating(report_id=statement.id,
                                                user_id=create_user.id)

    assert_that(result.total_income, equal_to(total_income))
    assert_that(result.total_expenditure, equal_to(total_expenditure))
    assert_that(result.grade, equal_to(expected_grade))


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


def test_calculate_period_rating_success(rating_service, create_user,
                                         create_statements_for_period):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=15)
    end_date = now

    response: RatingResponse = rating_service.calculate_period_rating(
        user_id=create_user.id,
        start_date=start_date,
        end_date=end_date
    )

    assert_that(response.total_income, equal_to(19500.0))
    assert_that(response.total_expenditure, equal_to(4500.0))
    assert_that(response.disposable_income, equal_to(15000.0))
    assert_that(response.grade, equal_to("B"))


def test_calculate_period_rating_no_statements(rating_service, create_user):
    start_date = datetime.now(timezone.utc) - timedelta(days=100)
    end_date = datetime.now(timezone.utc) - timedelta(days=50)

    with pytest.raises(StatementNotFoundError):
        rating_service.calculate_period_rating(
            user_id=create_user.id,
            start_date=start_date,
            end_date=end_date
        )


def test_calculate_period_rating_user_not_found(rating_service):
    with pytest.raises(UserNotFoundError):
        rating_service.calculate_period_rating(
            user_id=9999,
            start_date=datetime.now(timezone.utc) - timedelta(days=10),
            end_date=datetime.now(timezone.utc)
        )


def test_calculate_period_rating_only_start_date(rating_service, create_user,
                                                 create_statements_for_period):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=6)

    response: RatingResponse = rating_service.calculate_period_rating(
        user_id=create_user.id,
        start_date=start_date,
        end_date=None
    )

    assert_that(response.total_income,
                equal_to(13000.0))
    assert_that(response.total_expenditure, equal_to(3000.0))
    assert_that(response.grade, equal_to("B"))


def test_calculate_period_rating_only_end_date(rating_service, create_user,
                                               create_statements_for_period):
    now = datetime.now(timezone.utc)
    end_date = now - timedelta(days=7)

    response: RatingResponse = rating_service.calculate_period_rating(
        user_id=create_user.id,
        start_date=None,
        end_date=end_date
    )

    assert_that(response.total_income, equal_to(6500.0))
    assert_that(response.total_expenditure, equal_to(1500.0))
    assert_that(response.grade, equal_to("B"))
