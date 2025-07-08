from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class MenuButton(Base):
    __tablename__ = "menu_buttons"

    id = Column(Integer, primary_key=True)
    text = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("menu_buttons.id"))
    
    parent = relationship("MenuButton", remote_side=[id])
    children = relationship("MenuButton", back_populates="parent")