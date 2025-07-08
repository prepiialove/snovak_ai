from typing import Optional, Union
from pydantic import BaseModel

class RawText(BaseModel):
    text: str

class CategoryData(BaseModel):
    name: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True

class ServiceData(BaseModel):
    name: str
    category: Union[CategoryData, str]
    address: Optional[str] = None
    phone: Optional[str] = None
    schedule: Optional[str] = None
    social_media: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True