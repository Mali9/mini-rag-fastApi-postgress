from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponsesMessages
import random
import string
import re
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        
        
    def validate_file(self, file = UploadFile):
        # Get file extension from filename
        if not file.filename:
            return False, ResponsesMessages.FILE_TYPE_NOT_SUPPORTED.value
        
        file_extension = file.filename.split('.')[-1].lower()
        print(f"File extension: {file_extension}, Allowed extensions: {self.app_settings.FILE_ALLOWED_EXTENSIONS}")
        
        if file_extension not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponsesMessages.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > (self.app_settings.FILE_MAX_SIZE * 1024 * 1024):
            return False, ResponsesMessages.FILE_SIZE_LIMIT_EXCEEDED.value
     
        return True, ResponsesMessages.SUCCESS.value        
    
    
    def clean_file_name(self, file_name):
        #generate random string of 10 characters
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        file_name =  random_string + "_" + file_name
        #remove spaces and special characters using regex
        return file_name.replace(" ", "_")