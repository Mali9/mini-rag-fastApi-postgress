from enum import Enum
class DatabaseEnum(Enum):
    """
    Enum for database collection names
    """
    PROJECTS_COLLECTION_NAME = "projects"
    CHUNKS_COLLECTION_NAME = "chunks"
    ASSET_COLLECTION_NAME = "asset"