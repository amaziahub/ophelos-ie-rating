import logging

from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException

from service.schemas.statement_schema import StatementRequest, StatementCreateResponse
from service.statements.statement_service import create_statement_service

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("", response_model=StatementCreateResponse,
             status_code=status.HTTP_201_CREATED)
def create_statement(statement_data: StatementRequest):
    try:
        statement = create_statement_service(statement_data)
        return StatementCreateResponse(statement_id=statement.id)
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LookupError as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
