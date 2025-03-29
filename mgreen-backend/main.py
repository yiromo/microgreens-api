from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from global_router import router
from utils.init_migration import init_migration

app = FastAPI(
    title="MICROGREENS API",
    version="1.0.1",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    # await init_migration()
    pass

@app.get("/healthcheck/", include_in_schema=False)
async def healtcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)