"""
运行浏览器GUI
"""

import os, sys
from pathlib import Path

here = Path(__file__).parent

from HaiChatGPT.src.browser.app import run as run_app

def run():
    run_app(host='0.0.0.0', port=5000, debug=True)
    # dir_ = f'{here}/HaiChatGPT/src/browser'
    # os.chdir(dir_)
    # os.system('flask run')
    # os.chdir(str(here))


if __name__ == '__main__':
    run()

