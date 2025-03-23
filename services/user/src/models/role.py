from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from config.db import Base
from datetime import datetime

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"