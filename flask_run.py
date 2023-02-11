"""
运行浏览器GUI
"""

import os, sys
from pathlib import Path
import argparse

here = Path(__file__).parent

from HaiChatGPT.src.browser.app import run as run_app

def run(opt):
    # dir_ = f'{here}/HaiChatGPT/src/browser'
    # os.chdir(dir_)
    # run_app(host='0.0.0.0', port=5000, debug=True)
    run_app(host=opt.host, port=opt.port, debug=opt.debug)
    # os.chdir(str(here))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', type=bool, default=False)
    opt = parser.parse_args()
    run(opt)

