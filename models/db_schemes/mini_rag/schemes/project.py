import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .minirag_base import Base

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String, nullable=True)
    project_description = Column(String, nullable=True)
    project_uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4,unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=False,default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),nullable=False,default=datetime.now)
    
    # Relationships
    assets = relationship("Asset", back_populates="project")
    data_chunks = relationship("DataChunks", back_populates="project")