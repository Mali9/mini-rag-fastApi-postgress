from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from models import FileExtentionsEnum
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):
    def __init__(self,project_id = int):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id)
        
    def get_file_extension(self,file_name):
        return os.path.splitext(file_name)[-1]
    
    def get_file_loader(self,file_name:str):
        file_path = os.path.join(self.project_path,file_name)
        file_ext = self.get_file_extension(file_name)
        if file_ext == FileExtentionsEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        elif file_ext == FileExtentionsEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        else:
            return None
        
    def get_file_content(self,file_name:str):
        file_loader = self.get_file_loader(file_name)
        if file_loader is not None:
            return file_loader.load()
        else:
            return None
        
    def process_file_content(self,file_content : list,chunk_size:int=1000, chunk_overlap:int=200):
        """
        The process_file_content function processes the content of a file.
        It takes in a list of files and returns a list of chunks.
        The function uses the RecursiveCharacterTextSplitter to split the content into chunks.
        The function also creates a list of metadata for each chunk.
        The function returns a list of chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        file_content_list = [
            rec.page_content
            for rec in file_content
        ]
        
        file_metadata_list = [
            rec.metadata
            for rec in file_content
        ]
                
        chunks = text_splitter.create_documents(file_content_list,metadatas=file_metadata_list)
        return chunks
        
        
    