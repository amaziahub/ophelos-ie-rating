from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException

from service.schemas.statement_schema import StatementRequest, StatementResponse
from service.statements.statement_service import create_statement_service

router = APIRouter()


@router.post("", response_model=StatementResponse, status_code=status.HTTP_201_CREATED)
def create_statement(statement_data: StatementRequest):
    try:
        return create_statement_service(statement_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
