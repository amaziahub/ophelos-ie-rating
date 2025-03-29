from fastapi import Depends
from sqlalchemy.orm import Session

from service.db import get_db
from service.greeter.greeter_service import GreeterService
from service.users.user_service import UserService


def get_greeter_service(db: Session = Depends(get_db)) -> GreeterService:
    return GreeterService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
