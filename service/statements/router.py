import logging

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.exceptions import HTTPException

from service.dependencies import get_statement_service
from service.schemas.statement_schema import StatementRequest, \
    StatementCreateResponse, StatementResponse
from service.statements.statement_service import StatementService, \
    StatementNotFoundError, EmptyStatementError

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
    except (ValueError, EmptyStatementError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{statement_id}", response_model=StatementResponse,
            status_code=status.HTTP_200_OK)
def get_statement(
    statement_id: int,
    user_id: int,
    service: StatementService = Depends(get_statement_service)
):
    try:
        statement = service.get_statement(statement_id=statement_id, user_id=user_id)
        statement_data = jsonable_encoder(statement)
        return StatementResponse.model_validate(statement_data)
    except StatementNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Statement not found")
