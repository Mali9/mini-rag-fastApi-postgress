from typing import Optional
from pydantic import BaseModel

class ProcessData(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 10
    do_reset: Optional[int] = 0