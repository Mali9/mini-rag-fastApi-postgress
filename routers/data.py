from fastapi import APIRouter,Depends,UploadFile,Request
from helpers.config import *
from fastapi.responses import JSONResponse
from fastapi import status
from controllers import DataController
import os
from controllers import ProjectController
import aiofiles
from datetime import datetime
import logging
from routers.schemes.data import ProcessData
from controllers import ProcessController
from models.ProjectModel import ProjectModel
from models.ChunkDataModel import ChunkDataModel
from models.db_schemes.mini_rag.schemes import Project
from models.db_schemes.mini_rag.schemes import DataChunks
from models.db_schemes.mini_rag.schemes import Asset
from models.AssetModel import AssetModel
from sqlalchemy import select, func
logger = logging.getLogger(__name__)

data_router = APIRouter(prefix="/api/v1/data",tags=["data api's"])

@data_router.get("/project_stats/{project_id}")
async def get_project_stats(request: Request, project_id: int):
    try:
        asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
        chunk_model = await ChunkDataModel.create_instance(db_client=request.app.db_client)
        
        file_count = await asset_model.count_files_by_project_id(project_id)
        chunk_count = await chunk_model.count_chunks_by_project_id(project_id)
        
        return JSONResponse(
            content={
                "project_id": project_id,
                "file_count": file_count,
                "chunk_count": chunk_count
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting project stats: {e}")
        return JSONResponse(
            content={"message": f"Error getting project stats: {str(e)}"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

@data_router.get("/projects_with_stats")
async def get_projects_with_stats(request: Request):
    try:
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
        chunk_model = await ChunkDataModel.create_instance(db_client=request.app.db_client)
        
        projects, page, total_pages = await project_model.get_projects()
        
        # Get stats for each project
        projects_with_stats = []
        for project in projects:
            file_count = await asset_model.count_files_by_project_id(project.project_id)
            chunk_count = await chunk_model.count_chunks_by_project_id(project.project_id)
            
            project_dict = {
                "project_id": project.project_id,
                "project_uuid": str(project.project_uuid),
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                "file_count": file_count,
                "chunk_count": chunk_count
            }
            projects_with_stats.append(project_dict)
        
        return JSONResponse(
            content={
                "projects": projects_with_stats, 
                "page": page, 
                "total_pages": total_pages
            }, 
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting projects with stats: {e}")
        return JSONResponse(
            content={"message": f"Error getting projects with stats: {str(e)}"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

@data_router.post("/upload/{project_id}")
async def upload_data(request:Request,project_id:int,file:UploadFile,app_settings:Settings=Depends(get_settings)):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_new(project_id=project_id)
    is_valid , message = DataController().validate_file(file)
    if not is_valid:
        return JSONResponse(content={"is_valid":is_valid,"message":message},status_code=status.HTTP_400_BAD_REQUEST)
    project_dir = ProjectController().get_project_path(project_id = project_id)   
    file_name = DataController().clean_file_name(file.filename)
    file_path = os.path.join(project_dir, file_name)
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(app_settings.FILE_CHUNK_SIZE):
                await out_file.write(content)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(content={"is_valid":is_valid,"message":'file upload failed.'},status_code=status.HTTP_400_BAD_REQUEST)
    
    
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    asset_resource = Asset(
        asset_name=file_name,
        asset_type="file",
        asset_project_id=project.project_id,
        asset_size=os.path.getsize(file_path),
        asset_path=file_path,
    )
    asset_record = await asset_model.create_asset(asset=asset_resource)
    
    return JSONResponse(content={"file_name":file_name,"message":message,'project_id': str(project.project_id)}
                        ,status_code=status.HTTP_200_OK)

@data_router.get("/chunks")
async def get_chunks(request: Request, page: int = 1, limit: int = 20):
    chunk_model = await ChunkDataModel.create_instance(db_client=request.app.db_client)
    chunks = await chunk_model.get_all_chunks(page=page, limit=limit)
    # Get total count for all chunks
    async with chunk_model.db_client() as session:
        async with session.begin():
            query = select(func.count(DataChunks.chunk_id))
            total_count = await session.execute(query)
            total_count = total_count.scalar_one()
    
    return JSONResponse(content={
        "chunks": chunks,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }, status_code=status.HTTP_200_OK)

@data_router.get("/chunks/{project_id}")
async def get_chunks_by_project(request: Request, project_id: int, page: int = 1, limit: int = 20):
    chunk_model = await ChunkDataModel.create_instance(db_client=request.app.db_client)
    chunks = await chunk_model.get_project_chunks(project_id=project_id, page_no=page, page_size=limit)
    total_count = await chunk_model.count_chunks_by_project_id(project_id=project_id)
    chunks_dict = [
        {
            "chunk_id": chunk.chunk_id,
            "chunk_text": chunk.chunk_text,
            "chunk_metadata": chunk.chunk_metadata,
            "chunk_order": chunk.chunk_order,
            "chunk_asset_id": chunk.chunk_asset_id,
            "chunk_project_id": chunk.chunk_project_id,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
            "updated_at": chunk.updated_at.isoformat() if chunk.updated_at else None
        }
        for chunk in chunks
    ]
    return JSONResponse(content={
        "chunks": chunks_dict,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }, status_code=status.HTTP_200_OK)

@data_router.post("/process/{project_id}")
async def process_data(request: Request, project_id: int, data: ProcessData, app_settings: Settings = Depends(get_settings)):
    
    try:
        do_reset = data.do_reset
        file_id = data.file_id
        process_controller = ProcessController(project_id=project_id)      
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        project = await project_model.get_project_or_create_new(project_id=project_id)
        
        if data.file_id:
            project_file_ids = [file_id]
            asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
            asset = await asset_model.get_asset_by_name(file_id)
            if not asset:
                return JSONResponse(
                    content={"message": f"Asset not found for file_id: {file_id}"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            assets = [asset]
        else:
            asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
            assets = await asset_model.get_all_assets_by_project_id(project_id=project.project_id, asset_type='file')
            project_file_ids = [asset.asset_name for asset in assets]

        # Now assets is always defined
        asset_name_to_id = {str(asset.asset_name): asset.asset_id for asset in assets if asset}

        if len(project_file_ids) == 0:
            return JSONResponse(
                content={"message": 'no files found.'},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        number_of_files = 0
        chunk_len = 0
        chunk_model = await ChunkDataModel.create_instance(db_client=request.app.db_client)
        if do_reset == 1:
            no_deleted_record = await chunk_model.delete_chunks_by_project_id(project_id=project.project_id)
        else:
            no_deleted_record = 0
        # Build a mapping from asset_name to asset.id for quick lookup (now Asset objects)
        # asset_name_to_id = {str(asset.asset_name): asset.id for asset in assets} # This line is now redundant

        for file_name in project_file_ids:
            file_content = process_controller.get_file_content(file_name=file_name)
            chunks = process_controller.process_file_content(file_content=file_content)
            if not chunks:
                continue

            asset_id = asset_name_to_id.get(file_name)
            if not asset_id:
                logger.warning(f"No asset_id found for file: {file_name}")
                continue

            file_chunk_records = [
                DataChunks(
                    chunk_project_id=project.project_id,
                    chunk_order=i + 1,
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_asset_id=asset_id
                )
                for i, chunk in enumerate(chunks)
            ]
            chunk_len += await chunk_model.insert_many_chunks(file_chunk_records)
            number_of_files += 1
          
        return JSONResponse(
                content={
                    "message": 'data processed.',
                    "chunk_len": chunk_len,
                    'no_deleted_record': no_deleted_record,
                    'number_of_files': number_of_files  # optional, for clarity
                },
                status_code=status.HTTP_200_OK)      
    except Exception as e:
        logger.error(f"Error while processing data: {e}")
        return JSONResponse(
            content={"message": f"Error processing data: {str(e)}"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
 
@data_router.get("/get_all_projects")
async def get_all_projects(request: Request):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    projects, page, total_pages = await project_model.get_projects()
    # Convert SQLAlchemy objects to dictionaries
    projects_dict = [
        {
            "project_id": project.project_id,
            "project_uuid": str(project.project_uuid),
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        }
        for project in projects
    ]
    return JSONResponse(content={"projects": projects_dict, "page": page, "total_pages": total_pages}, status_code=status.HTTP_200_OK)

@data_router.post("/create_project")
async def create_project(request: Request):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.create_project(Project(project_id=1))
    # Convert SQLAlchemy object to dictionary
    project_dict = {
        "project_id": project.project_id,
        "project_uuid": str(project.project_uuid),
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None
    }
    return JSONResponse(content={"project": project_dict}, status_code=status.HTTP_200_OK)

@data_router.get("/files")
async def get_files(request: Request):
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    assets = await asset_model.get_all_assets(asset_type='file')
    assets_dict = [
        {
            "asset_id": asset.asset_id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "asset_project_id": asset.asset_project_id,
            "asset_size": asset.asset_size,
            "asset_path": asset.asset_path
        }
        for asset in assets
    ]
    
    return JSONResponse(content={"assets": assets_dict}, status_code=status.HTTP_200_OK)

@data_router.get("/files/{project_id}")
async def get_files_by_project(request: Request, project_id: int):
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    assets = await asset_model.get_all_assets_by_project_id(project_id=project_id, asset_type='file')
    assets_dict = [
        {
            "asset_id": asset.asset_id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "asset_project_id": asset.asset_project_id,
            "asset_size": asset.asset_size,
            "asset_path": asset.asset_path
        }
        for asset in assets
    ]
    
    return JSONResponse(content={"assets": assets_dict}, status_code=status.HTTP_200_OK)

@data_router.get("/generate_text")
def generate_text(request: Request, prompt: str):
    try:
        # Access the generation_client from the app instance
        generation_client = request.app.generation_client
        embedding_client = request.app.embedding_client
        if not prompt:
            return JSONResponse(
                content={"message": f"Prompt is required."},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        # Use the provided prompt
        
        generated_text = generation_client.generate_text(prompt=prompt)
        embeded_text = embedding_client.emebed_text(text=prompt)
        return JSONResponse(
                content={"generated_text": generated_text,'embeded_text':embeded_text},
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        logger.error(f"Error while processing data: {e}")
        return JSONResponse(
            content={"message": f"Error processing data: {str(e)}"},
            status_code=status.HTTP_400_BAD_REQUEST
        )