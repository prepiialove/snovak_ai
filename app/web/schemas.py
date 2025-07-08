from pydantic import BaseModel

class RawText(BaseModel):
    text: str

class CategoryData(BaseModel):
    name: str
    icon: str | None = None

    class Config:
        from_attributes = True

class ServiceData(BaseModel):
    name: str
    category: CategoryData | str
    address: str | None = None
    phone: str | None = None
    schedule: str | None = None
    social_media: str | None = None
    description: str | None = None

    class Config:
        from_attributes = True