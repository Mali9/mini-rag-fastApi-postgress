from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Index
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .minirag_base import Base
from sqlalchemy.orm import relationship

class DataChunks(Base):
    __tablename__ = "data_chunks"
    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=False)
    chunk_order = Column(Integer, nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)
    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=False,default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),nullable=False,default=datetime.now)
    
    asset = relationship("Asset", back_populates="data_chunks")
    project = relationship("Project", back_populates="data_chunks")
    
    __table_args__ = (
        Index("idx_chunk_project_id", chunk_project_id),
        Index("idx_chunk_asset_id", chunk_asset_id),
    )

class RetrivedDataChunks:
    def __init__(self, text: str, score: float,metadata:dict):
        self.text = text
        self.score = score
        self.metadata = metadata
    
    def dict(self):
        return {
            "text": self.text,
            "score": self.score,
            "metadata": self.metadata
        }