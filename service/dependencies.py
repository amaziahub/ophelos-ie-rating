from fastapi import Depends
from sqlalchemy.orm import Session
from service.db import get_db
from service.ratings.rating_service import RatingService
from service.statements.statement_service import StatementService
from service.users.user_service import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_statement_service(
        user_service: UserService = Depends(get_user_service),
        db: Session = Depends(get_db)
) -> StatementService:
    return StatementService(user_service=user_service, db=db)


def get_rating_service(db: Session = Depends(get_db),
                       statement_service: StatementService =
                       Depends(get_statement_service)) -> RatingService:
    return RatingService(db=db, statement_service=statement_service)
