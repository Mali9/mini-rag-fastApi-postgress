from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import DistanceType
from qdrant_client import models, QdrantClient
from typing import List, Dict, Any
import uuid
class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path:str,distance_method:str):
        self.db_path = db_path
        self.client = None
        self.distance_method = None
        if distance_method == DistanceType.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceType.DOT.value:
            self.distance_method = models.Distance.DOT
            
    async def connect(self):
        self.client = QdrantClient(path=self.db_path)
        # return self.client
    async def disconnect(self):
        self.client = None
        
    async def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name = collection_name)
    
    async def list_all_collections(self):
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name = collection_name)
    
    async def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name = collection_name)
    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name)
        
        if not self.is_collection_exists(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method)
            )
            return True
        return False
    
    async def insert_one(self, collection_name: str, text : str, vector: list , metadata: dict = None,record_id: str = None):
        if self.is_collection_exists(collection_name):
            return False
        
        _= self.client.upload_records(
            collection_name=collection_name,
            records=[
                models.Record(
                    payload={
                        "id":[record_id],
                        "text": text,
                        "metadata": metadata
                    },
                    vector=vector
                )
            ]
        )
        return True


    async def insert_many(self, collection_name: str, texts: List[str], vectors: list, metadata: list = None, record_ids: list = None , batch_size: int = 50):
        if not self.is_collection_exists(collection_name):
            return False
        if len(texts) != len(vectors):
            raise Exception("texts and vectors must have the same length")
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = list(range(0, len(texts)))
     
        for i in range(0, len(texts), batch_size):
            batch = []
            batch_end = i + batch_size
            text_batch = texts[i:batch_end]
            vector_batch = vectors[i:batch_end]
            metadata_batch = metadata[i:batch_end]
            record_ids_batch = record_ids[i:batch_end]
            batch=[
                models.Record(
                    payload={
                        "text": text_batch[x],
                        "metadata": metadata_batch[x]
                    },
                    vector=vector_batch[x],
                    id=record_ids_batch[x]
                )
                for x in range(0, len(text_batch))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch
                )
            except Exception as e:
                print(e)
                return False
        return True
    
    
    async def search_by_vector(self, collection_name: str, vector: list,limit: int = 10):
        if not self.is_collection_exists(collection_name):
            return []
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        