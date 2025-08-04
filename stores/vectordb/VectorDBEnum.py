from enum import Enum
class VectorDBType(Enum):
    QDRANT = "QDRANT"
    
class DistanceType(Enum):
    COSINE = "Cosine"
    DOT = "Dot"