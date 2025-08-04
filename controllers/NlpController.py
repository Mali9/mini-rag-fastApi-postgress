from .BaseController import BaseController
from models.db_schemes.mini_rag.schemes import Project
from models.db_schemes.mini_rag.schemes import DataChunks , RetrivedDataChunks
from typing import List, Dict
import json
class NlpController(BaseController):
    def __init__(self,vectordb_client,generation_client,embedding_client,template_parser):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    

    def create_collection_name(self, project_id):
        return f"collection_{project_id}".strip()
    
    def delete_collection(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_collection_info(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda o: o.__dict__)
        )

    def index_into_vectordb(self, project:Project, chunks:List[DataChunks],do_reset:bool = False,chunks_ids:List[int] = []):
            collection_name = self.create_collection_name(project_id=project.project_id)
            # Get embedding size from embedding_client if possible, else from config
            embedding_size = self.embedding_client.embedding_size 
            # Create/reset collection if needed
            self.vectordb_client.create_collection(collection_name=collection_name, embedding_size=embedding_size, do_reset=do_reset)
            # Prepare data for batch insert
            texts = [chunk.chunk_text for chunk in chunks]
            vectors = [self.embedding_client.emebed_text(chunk.chunk_text) for chunk in chunks]
            metadatas = [chunk.chunk_metadata for chunk in chunks]
            # INSERT_YOUR_CODE
            # Write chunks to a file for debugging or record-keeping
            with open("chunks_output.txt", "w", encoding="utf-8") as f:
                for chunk in chunks:
                    f.write(f"ID: {getattr(chunk, 'id', 'N/A')}\n")
                    f.write(f"Text: {chunk.chunk_text}\n")
                    f.write(f"vectors: {vectors}\n")
                    f.write(f"Metadata: {chunk.chunk_metadata}\n")
                    f.write("-" * 40 + "\n")
            # Insert into vectordb
            result = self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                metadata=metadatas,
                record_ids=chunks_ids
            )
            return True
    def search(self, project:Project, query:str, limit:int = 5):
        collection_name = self.create_collection_name(project_id=project.project_id)
        # Prepare query embedding
        vector = self.embedding_client.emebed_text(query)
        
        if not vector or len(vector) == 0:
            return []
        # Perform search
        results = self.vectordb_client.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)
        if not results:
            return None
        
        # Convert every result to RetrievedDataChunks
        retrieved_chunks = []
        for res in results:
            # Assuming res is a dict with keys matching RetrievedDataChunks fields
            retrieved_chunk = RetrivedDataChunks(
                text=res.payload["text"],
                score=res.score,
                metadata=res.payload["metadata"]
            )
            retrieved_chunks.append(retrieved_chunk)
        return retrieved_chunks
        
    def ansewr_rag_question(self, project:Project, query:str, limit:int = 5):
        answer, full_prompt, chat_history = None, None, []
        # Perform search
        retrieved_restults = self.search(project=project, query=query, limit=limit)
        if not retrieved_restults:
            return None
        system_prompt = self.template_parser.get(group="rag", key="system_prompt")

        documents_prompt = "\n".join([
            self.template_parser.get(group="rag", key="document_prompt", vars={
                    "doc_no": idx+1,
                    "text": chunk.text
                })
            for idx, chunk in enumerate(retrieved_restults)
        ])
        footer_prompt = self.template_parser.get(group="rag", key="footer_prompt")

        # Prepare chat history for Ollama chat API
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
            ),
            {"role": "user", "content": documents_prompt},
        ]
        # The actual user question as the last message
        user_question_message = {"role": "user", "content": query}

        answer = self.generation_client.generate_text(
            prompt=footer_prompt,  # The footer prompt (e.g., 'You Answer:')
            chat_history=chat_history + [user_question_message]
        )

        return answer