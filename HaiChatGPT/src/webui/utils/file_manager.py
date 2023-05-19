"""
用来处理用户上传的文件的工具类
"""
import os, sys
from pathlib import Path
import damei as dm
import json
from ....version import __appname__
from .cal_num_tokens import cal_num_tokens


class FileManager(object):

    def __init__(self) -> None:
        self._user_file_dir = f'{Path.home()}/.{__appname__}/user_files'
        self._make_dir(self._user_file_dir)
    
    def _make_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def get_file_path(self, username, filename, create_if_no_exist=False):
        return f'{self._user_file_dir}/{username}/{filename}'

    def process_uploaded_file(self, request, username=None):
        username = username or 'public'
        save_dir = f'{self._user_file_dir}/{username}'
        self._make_dir(save_dir)
        file = request.files['file']
        file_path = f'{save_dir}/{file.filename}'
        file.save(file_path)

        file_content = self.parse_file(file_path)

        num_tokens = cal_num_tokens(file_content)
        return file_content, num_tokens
    
    def parse_file(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()
        if file_path.endswith('.json'):
            data = json.loads(data)
            # 转换为字符串
            data = json.dumps(data, indent=4)
        elif file_path.endswith('.py'):
            pass
        elif file_path.endswith('.txt'):
            pass
        elif file_path.endswith('.md'):
            pass
        elif file_path.endswith('.pdf'):
            raise NotImplementedError('.pdf file is not supported yet.')
        elif file_path.endswith('.html'):
            pass
        else:
            raise NotImplementedError(f'file type {file_path} is not supported yet.')    
        
        print(f'data: {type(data)} {data}')
        return data

