from fastapi import APIRouter,Depends
from helpers.config import *
# import os
base_router = APIRouter(prefix="/api/v1",tags=["base api's"])

@base_router.get("/")
async def index(app_settings:Settings = Depends(get_settings)):
    # app_settings = get_settings()
    data = {'app_name': app_settings.APP_NAME,'app_version': app_settings.APP_VERSION}
    return data
