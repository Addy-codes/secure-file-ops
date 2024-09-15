from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.file.router import router as file_router
from src import config

app = FastAPI(
    title=config.PROJECT_TITLE,
    description=config.PROJECT_DESCRIPTION,
    version=config.PROJECT_VERSION,
)

app.include_router(auth_router, prefix="/auth")
app.include_router(file_router, prefix="/files")

@app.get("/")
async def root():
    return {"message": "Welcome to Secure File Ops by AddyCodes"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
