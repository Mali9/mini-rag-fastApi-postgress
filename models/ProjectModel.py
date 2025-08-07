from .BaseDataModel import BaseDataModel
from .enums.DatabaseEnum import DatabaseEnum
from models.db_schemes.mini_rag.schemes.project import Project
from sqlalchemy import select,func
from datetime import datetime
class ProjectModel(BaseDataModel):
    def __init__(self,db_client):
        super().__init__(db_client)
        self.db_client = db_client
        
    @classmethod
    async def create_instance(cls,db_client):
        instance = cls(db_client=db_client)
        return instance
     
    


       
    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        return project
                
        

    async def update_project(self, project_id: int, project_data: Project):
        async with self.db_client() as session:
            async with session.begin():  # Automatically commits or rolls back
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()

                if not project:
                    raise Exception("Project not found")

                project.project_name = project_data.project_name
                project.project_description = project_data.project_description
                project.updated_at = datetime.now()

            await session.refresh(project)  # This is okay outside the transaction

        return project

    
    async def get_project_or_create_new(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if not project:
                    project = await self.create_project(Project(project_id=project_id,project_name="Project Name" ,project_description="Project Description"))
                await session.refresh(project)
                await session.commit()
        return project
        

    async def get_last_project_id(self):
        async with self.db_client() as session:
            async with session.begin():
                query = select(func.max(Project.project_id))
                result = await session.execute(query)
                return result.scalar_one()
                
    async def get_project(self,project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                project = await query.scalar_one_or_none()
                if not project:
                    raise Exception("Project not found")
                await session.commit()
                await session.refresh(project)
        return project
    
    async def get_projects(self,page: int = 1,limit: int = 10):
        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(select(func.count(Project.project_id)))
                total_documents = total_documents.scalar_one()
                total_pages = total_documents // limit
                if total_documents % limit != 0:
                    total_pages += 1
                if page < 1 or page > total_pages:
                    raise Exception("Invalid page number")
                
                query = select(Project).offset((page-1)*limit).limit(limit)
                projects = await session.execute(query)
                projects = projects.scalars().all()
            return projects,page,total_pages
