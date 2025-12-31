import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# from redis.asyncio import Redis

# from infrastructure.config.app import AppConfig
# from domain.exceptions import AuthException
# from server.dependencies import config, redis_client, get_session, get_redis

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     import server.dependencies as deps
#     redis_url = config.redis.build_url()
#     deps.redis_client = await Redis.from_url(redis_url, decode_responses=True)
#     yield
#     await deps.redis_client.close()


# app = FastAPI(
#     title="Trading API",
#     version="1.0.0",
#     lifespan=lifespan,
#     debug=config.app_mode == "development"
# )


# @app.exception_handler(AuthException)
# async def auth_exception_handler(request, exc: AuthException):
#     return JSONResponse(
#         status_code=401,
#         content={"detail": str(exc)},
#     )


# from server.routes import auth_router
# app.include_router(auth_router)


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         reload=config.app_mode == "development"
#     )


import asyncio
from domain.models.logic import TimeFrame
from infrastructure.services.moex.moex_data_service import MoexDataService
from apscheduler.triggers.cron import CronTrigger
from infrastructure.services.background.background_service import BackgroundService
from infrastructure.services.background.service_manager import ServiceManager
from infrastructure.services.trade.fetch_service import TradeFetchService

async def main():

    cron = CronTrigger(minute=0, second=0)
    task = TradeFetchService(cron)

    service = BackgroundService(
        name="tarade_fetch",
        func=task,
        cron=cron
    )

    manager = ServiceManager()
    manager.add_service(service)

    manager.run_now("tarade_fetch")

    manager.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Прерывание пользователем, завершение работы...")
    except asyncio.CancelledError:
        print("Асинхронная задача была отменена")
    finally:
        print("Main loop закрыт")
