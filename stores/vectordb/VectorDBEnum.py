from enum import Enum
class VectorDBType(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"
    
class DistanceType(Enum):
    COSINE = "Cosine"
    DOT = "Dot"

class VectorDBDistanceType(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class VectorDBTableField(Enum):
    ID = "id"
    CHUNK_ID = "chunk_id"
    TEXT = "text"
    VECTOR = "vector"
    METADATA = "metadata"
    _PREFIX = "pgvector_"

class VectorDBIndexType(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"
 
