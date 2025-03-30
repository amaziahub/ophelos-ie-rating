from operator import is_not

import pytest
from hamcrest import assert_that, none, equal_to

from service.schemas.user_schema import UserCreate
from service.users.user_service import UserService


@pytest.fixture
def user_service(db):
    return UserService(db)


def test_create_user(user_service):
    user_data = UserCreate(username="steve", password="minecraft")
    user = user_service.create_user(user_data)

    is_not(user, none())
    assert_that(user.username, equal_to("steve"))
    is_not(user.id, none())


def test_get_user_by_username(user_service):
    user_data = UserCreate(username="alex", password="minecraft")
    user_service.create_user(user_data)

    retrieved_user = user_service.get_user_by_username("alex")
    is_not(retrieved_user, none())
    assert_that(retrieved_user.username, equal_to("alex"))


def test_get_user_by_id(user_service):
    user_data = UserCreate(username="creeper", password="minecraft")
    created_user = user_service.create_user(user_data)

    retrieved_user = user_service.get_user_by_id(created_user.id)
    is_not(retrieved_user, none())
    assert_that(retrieved_user.username, equal_to("creeper"))
