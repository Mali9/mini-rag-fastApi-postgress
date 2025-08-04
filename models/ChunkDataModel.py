from .BaseDataModel import BaseDataModel
from .enums.DatabaseEnum import DatabaseEnum
from models.db_schemes.mini_rag.schemes.data_chunks import DataChunks
from sqlalchemy import select, func, delete
class ChunkDataModel(BaseDataModel):
    def __init__(self,db_client):
        super().__init__(db_client)
        self.db_client = db_client
     
    @classmethod
    async def create_instance(cls,db_client):
        instance = cls(db_client=db_client)
        return instance
    
    async def create_chunk(self, chunk: DataChunks):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk
    
    async def get_chunk(self, chunk_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunks).where(DataChunks.chunk_id == chunk_id)
                chunk = await session.execute(query)
                chunk = chunk.scalar_one_or_none()
                if not chunk:
                    raise Exception("Chunk not found")
        return chunk
    
    async def get_project_chunks(self, project_id: int, page_no: int = 1, page_size: int = 50):
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunks).where(DataChunks.chunk_project_id == project_id)
                query = query.offset((page_no-1)*page_size).limit(page_size)
                chunks = await session.execute(query)
                chunks = chunks.scalars().all()
        return chunks

    async def insert_many_chunks(self, chunks: list):
        try:
            async with self.db_client() as session:
                async with session.begin():
                    session.add_all(chunks)
                await session.commit()
            return len(chunks)
        except Exception as e:
            raise e
    
    async def get_chunks(self, chunk_ids: list[int]):
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunks).where(DataChunks.chunk_id.in_(chunk_ids))
                chunks = await session.execute(query)
                chunks = chunks.scalars().all()
        return chunks
    
    async def delete_chunks_by_project_id(self, project_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = delete(DataChunks).where(DataChunks.chunk_project_id == project_id)
                result = await session.execute(query)
                await session.commit()
        return result.rowcount
    
    async def count_chunks_by_project_id(self, project_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = select(func.count(DataChunks.chunk_id)).where(DataChunks.chunk_project_id == project_id)
                count = await session.execute(query)
                count = count.scalar_one()
        return count