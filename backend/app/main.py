from fastapi import FastAPI
from app.routers.machine_router import router as machine_router
from app.routers.package_router import router as package_router
from app.routers.distribucion_router import router as distribucion_router
from app.routers.estilo_router import router as estilo_router

app = FastAPI(
    title="CLASIFICADOR STD - Sistema Experto",
    version="2.0.0"
)

@app.get("/")
def root():
    return {"message": "Backend Sistema Experto v2.0 - Listo"}

app.include_router(machine_router)
app.include_router(package_router)
app.include_router(distribucion_router)
app.include_router(estilo_router)