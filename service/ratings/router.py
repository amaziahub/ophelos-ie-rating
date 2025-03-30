from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.dependencies import get_statement_service, get_db
from service.schemas.rating_schema import RatingResponse
from service.statements.statement_service import StatementService, UserNotFoundError, \
    StatementNotFoundError
from service.ratings.rating_service import RatingService

router = APIRouter()


@router.get("", response_model=RatingResponse, status_code=status.HTTP_200_OK)
def calculate_rating(
        report_id: int,
        user_id: int,
        db: Session = Depends(get_db),
        statement_service: StatementService = Depends(get_statement_service)
):
    rating_service = RatingService(db=db, statement_service=statement_service)
    try:
        result = rating_service.calculate_ie_rating(report_id, user_id)
        return result
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    except StatementNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Statement not found")
