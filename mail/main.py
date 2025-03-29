from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="MAIL API",
    version="1.0.1",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["http://192.168.11.3:8000", "192.168.11.3:8000", "192.168.11.3", "http://192.168.11.3"],
)

@app.get("/healthcheck/", include_in_schema=False)
async def healtcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8030, reload=True)