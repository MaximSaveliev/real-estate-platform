from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, text, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False, onupdate=datetime.now)
    
    # Relationships
    role = relationship("Role")
    agent = relationship("Agent", uselist=False, back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"