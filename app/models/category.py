from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    icon = Column(String(50))  # Emoji or icon name

    services = relationship("Service", back_populates="category")