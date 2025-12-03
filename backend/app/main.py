from fastapi import FastAPI
from backend.app.routers.machine_router import router as machine_router
from backend.app.routers.package_router import router as package_router

app = FastAPI(
    title="CLASIFICADOR STD - Sistema Experto",
    version="2.0.0"
)

@app.get("/")
def root():
    return {"message": "Backend Sistema Experto v2.0 - Listo"}

app.include_router(machine_router)
app.include_router(package_router)