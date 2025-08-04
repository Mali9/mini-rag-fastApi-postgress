from .VectorDBInterface import VectorDBInterface
from .VectorDBEnum import VectorDBType, DistanceType
from .providor.QdrantDBProvider import QdrantDBProvider
import logging
from controllers.BaseController import BaseController
class VectorDBProviderFactory:
    """
    Factory class for creating Vector Database provider instances.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_controller = BaseController()
    
    def create_provider(self, provider: str | None, **kwargs):
        """
        Create a Vector Database provider instance based on the provider type.
        
        Args:
            provider (str | None): The type of Vector DB provider to create
            **kwargs: Additional arguments for the provider
            
        Returns:
            VectorDBInterface: An instance of the requested Vector DB provider
            
        Raises:
            ValueError: If an unsupported provider type is specified or provider is None
        """
        
        if provider is None:
            raise ValueError("Provider type cannot be None")
        
        if provider == VectorDBType.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)
            distance_method = self.config.VECTOR_DB_DISTANCE_METRIC
            return QdrantDBProvider(db_path=db_path, distance_method=distance_method)
             
        else:
            raise ValueError(f"Unsupported provider type: {provider}")
        
