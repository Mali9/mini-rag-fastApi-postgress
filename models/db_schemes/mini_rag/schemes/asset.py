from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Index
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .minirag_base import Base
from sqlalchemy.orm import relationship

class Asset(Base):
    __tablename__ = "assets"
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4,unique=True)
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=False)
    asset_path = Column(String, nullable=False)
    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=False,default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),nullable=False,default=datetime.now)
    
    
    project = relationship("Project", back_populates="assets")
    data_chunks = relationship("DataChunks", back_populates="asset")
    __table_args__ = (
        Index("idx_asset_project_id", asset_project_id),
    )