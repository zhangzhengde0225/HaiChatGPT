import os

import argparse

from HaiChatGPT import HaiChatGPT


def run_cli(args, **kwargs):
    """Run the command line interface."""
    HaiChatGPT.run_cli(**kwargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', action='store_true')
    args = parser.parse_args()

    args.cli = True

    run_cli(args)
