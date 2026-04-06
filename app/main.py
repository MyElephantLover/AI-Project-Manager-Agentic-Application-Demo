import asyncio
from fastapi import FastAPI

from app.poller import init_db, poll_once, POLL_INTERVAL_SECONDS

app = FastAPI()


async def polling_loop() -> None:
    while True:
        try:
            poll_once()
        except Exception as exc:
            print(f"Background polling error: {exc}")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


@app.on_event("startup")
async def startup_event() -> None:
    init_db()
    asyncio.create_task(polling_loop())


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}