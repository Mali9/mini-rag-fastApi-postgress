from .BaseDataModel import BaseDataModel
from .enums.DatabaseEnum import DatabaseEnum
from models.db_schemes.mini_rag.schemes.asset import Asset
from sqlalchemy import select, func
class AssetModel(BaseDataModel):
    def __init__(self,db_client):
        super().__init__(db_client)
        self.db_client = db_client
     
    @classmethod
    async def create_instance(cls,db_client):
        instance = cls(db_client=db_client)
        return instance
    
    async def create_asset(self, asset: Asset):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset
    
    async def get_all_assets_by_project_id(self, project_id: int, asset_type: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(Asset.asset_project_id == project_id, Asset.asset_type == asset_type)
                assets = await session.execute(query)
                assets = assets.scalars().all()
        return assets

    async def get_asset_by_id(self, asset_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(Asset.asset_id == asset_id)
                asset = await session.execute(query)
                asset = asset.scalar_one_or_none()
        return asset
    
    async def get_asset_by_name(self, asset_name: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(Asset.asset_name == asset_name)
                asset = await session.execute(query)
                asset = asset.scalar_one_or_none()
        return asset
    
    async def count_files_by_project_id(self, project_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = select(func.count(Asset.asset_id)).where(
                    Asset.asset_project_id == project_id, 
                    Asset.asset_type == 'file'
                )
                count = await session.execute(query)
                count = count.scalar_one()
        return count