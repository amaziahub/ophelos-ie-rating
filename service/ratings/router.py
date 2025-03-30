from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.dependencies import get_statement_service, get_db
from service.schemas.rating_schema import RatingResponse
from service.statements.statement_service import StatementService, UserNotFoundError, \
    StatementNotFoundError, USER_NOT_FOUND, STATEMENT_NOT_FOUND
from service.ratings.rating_service import RatingService

router = APIRouter()


@router.get("", response_model=RatingResponse, status_code=status.HTTP_200_OK)
def calculate_rating(
    report_id: Optional[int] = None,
    user_id: int = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    statement_service: StatementService = Depends(get_statement_service)
):
    rating_service = RatingService(db=db, statement_service=statement_service)
    try:
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        if report_id:
            result = rating_service.calculate_ie_rating(report_id, user_id)
        else:
            result = rating_service.calculate_period_rating(
                user_id, start_date, end_date)
        return result
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)
    except StatementNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=STATEMENT_NOT_FOUND)
