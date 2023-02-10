"""
运行浏览器GUI
"""

import os, sys
from pathlib import Path

here = Path(__file__).parent


def run():
    dir_ = f'{here}/HaiChatGPT/src/browser'

    os.chdir(dir_)

    os.system('flask run')
    
    os.chdir(str(here))

if __name__ == '__main__':
    run()

