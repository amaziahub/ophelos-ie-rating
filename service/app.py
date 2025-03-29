import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from service.db import Base, engine
from service.greeter import router as greeter_router
from service.health import router as health_router
from service.users.user_service import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(redirect_slashes=False)
Base.metadata.create_all(bind=engine)
UserService.insert_default_users()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


app.include_router(health_router.router, prefix="/health")
app.include_router(greeter_router.router, prefix="/greet")


def main():
    import uvicorn
    host = os.getenv("ENDPOINT", "localhost")
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
