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
        if report_id:
            result = rating_service.calculate_ie_rating(report_id, user_id)
        else:
            parsed_start_date = parse_iso_date(start_date)
            parsed_end_date = parse_iso_date(end_date)
            result = rating_service.calculate_period_rating(
                user_id, parsed_start_date, parsed_end_date)
        return result
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)
    except StatementNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=STATEMENT_NOT_FOUND)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def parse_iso_date(date_str: Optional[str]) -> Optional[datetime]:
    if date_str:
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. "
                             f"Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    return None
