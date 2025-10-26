import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from redis.asyncio import Redis

from infrastructure.config.app import AppConfig
from domain.exceptions import AuthException
from server.dependencies import config, redis_client, get_session, get_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    import server.dependencies as deps
    redis_url = config.redis.build_url()
    deps.redis_client = await Redis.from_url(redis_url, decode_responses=True)
    yield
    await deps.redis_client.close()


app = FastAPI(
    title="Trading API",
    version="1.0.0",
    lifespan=lifespan,
    debug=config.app_mode == "development"
)


@app.exception_handler(AuthException)
async def auth_exception_handler(request, exc: AuthException):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )


from server.routes import auth_router
app.include_router(auth_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=config.app_mode == "development"
    )


# from infrastructure.services.export_service import ExportService
# from infrastructure.services.moex.moex_logic import MoexLogicService
# from domain.model import TimeFrame

# if __name__ == "__main__":
#     ticker = "GAZP"
#     interval = TimeFrame.HOUR
#     from_date = "2025-01-01"
#     till_date = "2025-10-25"

#     logic = MoexLogicService()
#     df = logic.get_candles_with_range(ticker, interval, from_date, till_date)

#     print(df.tail())
#     print("Записей:", len(df))

#     path = ExportService.export_to_csv(df, ticker, interval.name, from_date, till_date)
#     print(f"CSV сохранён в: {path}")
