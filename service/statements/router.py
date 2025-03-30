import logging

from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException

from service.dependencies import get_statement_service
from service.schemas.statement_schema import StatementRequest, StatementCreateResponse
from service.statements.statement_service import StatementService

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("", response_model=StatementCreateResponse,
             status_code=status.HTTP_201_CREATED)
def create_statement(
    statement_data: StatementRequest,
    service: StatementService = Depends(get_statement_service)
):
    try:
        statement = service.create_statement(statement_data)
        return StatementCreateResponse(statement_id=statement.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
