import os

import argparse

from HaiChatGPT.src.runner import Runner, run


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy' , type=str, default=None, help='Proxy')
    parser.add_argument('--use-api-key', action='store_true', help='Use API key if True, use Access Token by default')
    parser.add_argument('--engine', type=str, default='text-davinci-003', help='Engine name, only used when use-api-key is True')
    opt = parser.parse_args()

    runner = Runner(opt)
    runner.run_cli()
