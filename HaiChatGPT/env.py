
import os
from pathlib import Path
from .version import __author__, __email__, __appname__


api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    # key_file = f'{Path.home()}/.openai/api_key'
    key_file = os.path.join(Path.home(), '.openai', 'api_key.txt')
    if not os.path.exists(key_file):
        raise ValueError(
            f'OPENAI_API_KEY not found. There are two ways to set it:\
                \n  1. Setting env variable "OPEN_API_KEY" to you API Key before run. \
                \n  2. Save your API Key to the file: {key_file}. \
                \n If you do not have an API Key, please visit https://openai.com/ to get one OR contact the {__appname__} author: {__author__}({__email__}).')
    with open(key_file, 'r') as f:
        api_key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = api_key
        
print(f"Use the API Key: {api_key[:5]}{'*' * (len(api_key) - 10)}{api_key[-5:]}")
