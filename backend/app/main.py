from fastapi import FastAPI
from backend.app.routers.fg_router import router as fg_router
from backend.app.routers.setup_router import router as setup_router

app = FastAPI(
    title="CLASIFICADOR STD - Sistema Experto",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Backend listo pa"}

app.include_router(fg_router)
app.include_router(setup_router)
