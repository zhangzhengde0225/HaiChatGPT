import os
import argparse
import logging



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy' , type=str, default=None, help='Proxy')
    parser.add_argument('--use-api-key', action='store_true', help='Use API key if True, use Access Token by default')
    parser.add_argument('--use-fake-bot', action='store_true', help='Use fake bot if True, use real bot by default')
    parser.add_argument('--engine', type=str, default='gpt-3.5-turbo-0301', help='Engine name, only used when use-api-key is True')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    opt = parser.parse_args()

    if opt.debug:
        os.environ["LOGGING_LEVEL"] = str(logging.DEBUG)
    else:
        os.environ['LOGGING_LEVEL'] = str(logging.INFO)

    from HaiChatGPT.src.runner import Runner, run
    runner = Runner(opt)
    runner.run_cli()
