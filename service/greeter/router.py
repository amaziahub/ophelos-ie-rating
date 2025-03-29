import logging

from fastapi import APIRouter, status, Depends

from service.dependencies import get_greeter_service
from service.greeter.greeter_service import GreeterService
from service.greeter.schemas.greet import Greeter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=Greeter, status_code=status.HTTP_201_CREATED)
def post_greet(greeter: Greeter,
               service: GreeterService = Depends(get_greeter_service)):
    saved_greeter = service.save_greet(greeter)
    logger.info(f"Received greet: {saved_greeter.greet_msg} from {saved_greeter.name}")
    return saved_greeter
