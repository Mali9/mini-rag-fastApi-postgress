from typing import Optional
from pydantic import BaseModel

class CreateProject(BaseModel):
    project_name: str
    project_description: Optional[str] = None
    