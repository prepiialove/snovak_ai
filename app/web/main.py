from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.schemas import RawText, ServiceData
from app.services.ai import get_service_data_from_text
from app.services.crud import create_service
from app.core.db import get_async_session

app = FastAPI(title="Snovsk Bot Admin Panel")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Snovsk Bot Admin Panel"}

@app.post("/process-text/", response_model=ServiceData)
async def process_text(raw_text: RawText):
    """
    Receives raw text, processes it with OpenAI, and returns structured data.
    """
    service_data = get_service_data_from_text(raw_text.text)
    if not service_data:
        raise HTTPException(status_code=500, detail="Failed to process text with AI")
    return service_data

@app.post("/services/", response_model=ServiceData)
async def add_service(
    service_data: ServiceData,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Adds a new service to the database.
    """
    service = await create_service(session, service_data.model_dump())
    return service