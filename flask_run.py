"""
运行浏览器GUI
"""

import os, sys
from pathlib import Path
import argparse
import logging
here = Path(__file__).parent



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--proxy' , type=str, default=None, help='Proxy')
    parser.add_argument('--use-api-key', action='store_true', help='Use API key if True, use Access Token by default')
    parser.add_argument('--engine', type=str, default='gpt-3.5-turbo-0301', help='Engine name, only used when use-api-key is True')
    parser.add_argument('--temperature', type=float, default=0.5, help='Temperature, 0 to 1, more is more random')
    parser.add_argument('--use-fake-bot', action='store_true', help='Use fakebot if true')
    parser.add_argument('--use-sso-auth', action='store_true', help='Use SSO auth if True')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    opt = parser.parse_args()

    if opt.debug:
        os.environ["LOGGING_LEVEL"] = str(logging.DEBUG)
    else:
        os.environ['LOGGING_LEVEL'] = str(logging.INFO)

    from HaiChatGPT.src.runner import Runner
    runner = Runner(opt)
    runner.run_webui()
