from fastapi import APIRouter,Depends,Request
from fastapi.responses import JSONResponse
from fastapi import status
from .schemes.nlp import PushRequest,SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkDataModel import ChunkDataModel
from controllers.NlpController import NlpController
from bson import ObjectId  # <-- Add this import 
nlp_router = APIRouter(prefix="/api/v1/nlp",tags=["nlp api's"])
@nlp_router.post("/push/{project_id}")
async def push_nlp(project_id: int, request: Request, push_request: PushRequest):
    try:
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        do_reset = push_request.do_reset
        project = await project_model.get_project_or_create_new(project_id=project_id)
        # return JSONResponse(status_code=status.HTTP_200_OK, content=project_dict)  # Remove this premature return
        if not project:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "project not found"})

        nlpController = NlpController(
            embedding_client=request.app.embedding_client,
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            template_parser=request.app.template_parser,
        )
        chunk_model = await ChunkDataModel.create_instance(db_client=request.app.db_client)
        page_no = 1
        has_record = True
        inserted_count = 0
        all_chunks = []  # Collect all chunks her
        idx = 0
        while has_record:
            chunk_data = await chunk_model.get_project_chunks(
                project_id=project.project_id,
                page_no=page_no,
            )            
            if len(chunk_data):
                page_no += 1
            if not chunk_data or len(chunk_data) == 0:
                has_record = False
                break
            
            chunks_ids = list(range(idx,idx + len(chunk_data)))
            idx += len(chunk_data)

            is_inserted = nlpController.index_into_vectordb(
                project=project,
                chunks=chunk_data,
                do_reset=do_reset,
                chunks_ids=chunks_ids,

            )
            if not is_inserted:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "failed to index into vectordb"})
            inserted_count += len(chunk_data)
            all_chunks.extend(chunk_data)  # Add chunks to the list

        # print(all_chunks)
        response_content = {
            "message": "success",
            "chunk_count": len(all_chunks)
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content,
        )
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
@nlp_router.get("/info/{project_id}")
async def get_project_info(project_id: int, request: Request):
    try:
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        project = await project_model.get_project_or_create_new(project_id=project_id)
        nlpController = NlpController(
            embedding_client=request.app.embedding_client,
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            template_parser=request.app.template_parser,
        )
        collection_info = nlpController.get_vector_collection_info(project=project)
        print(collection_info)
        response_content = {
            "message": "success",
            "collection_info": collection_info,
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content,
        )
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)})   
    
    
@nlp_router.post("/search/{project_id}")
async def search(project_id: int, request: Request,search_request: SearchRequest):
    try:
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        project = await project_model.get_project_or_create_new(project_id=project_id)
        nlpController = NlpController(
            embedding_client=request.app.embedding_client,
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            template_parser=request.app.template_parser,
        )
        text = search_request.text

        
        if not text:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "query is required"})
        results = nlpController.search(project=project, query=text,limit=5)
        
        response_content = {
            "message": "success",
            "results": [result.dict() for result in results]
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content,
        )
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
@nlp_router.post("/answer/{project_id}")
async def answer(project_id: int, request: Request,search_request: SearchRequest):
    try:
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        project = await project_model.get_project_or_create_new(project_id=project_id)
        nlpController = NlpController(
            embedding_client=request.app.embedding_client,
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            template_parser=request.app.template_parser,
        )
        text = search_request.text

        
        if not text:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "query is required"})
        results = nlpController.ansewr_rag_question(project=project, query=text,limit=5)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "success", "answer": results},
        )
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)})