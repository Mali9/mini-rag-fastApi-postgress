from helpers.config import get_settings
import os
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, 'assets/files')
        self.dabase_dir = os.path.join(self.base_dir, 'assets/database')
        
    def get_database_path(self, database_name):
        database_path = os.path.join(self.dabase_dir, database_name)
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path
    
    def get_project_path(self,project_id = int):
        project_dir = os.path.join(self.files_dir,'Project_' + str(project_id))
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        return project_dir
    