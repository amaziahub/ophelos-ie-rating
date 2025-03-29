from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class Health(BaseModel):
    status: str = 'OK'
    message: str = 'Service is up and running'


@router.get("", response_model=Health, status_code=status.HTTP_200_OK)
def health():
    return Health()
