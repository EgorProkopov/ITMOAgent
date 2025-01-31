import uvicorn
from fastapi import FastAPI

from app.containers import AppContainer
import app.api.endpoints as endpoints
from app.api.endpoints import router


def set_routers(app: FastAPI) -> None:
    app.include_router(router)


def create_app() -> FastAPI:
    container = AppContainer()
    container.wire(modules=[endpoints])

    app = FastAPI()
    app.container = container
    set_routers(app)
    return app


if __name__ == '__main__':
    app = create_app()
    uvicorn.run(app, port=8080)
