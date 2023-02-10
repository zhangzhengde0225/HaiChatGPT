import argparse

from HaiChatGPT import HaiChatGPT


def run_cli(**kwargs):
    """Run the command line interface."""
    HaiChatGPT.run_cli(**kwargs)

def run():
    chat = HaiChatGPT()
    chat.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', action='store_true')
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run()
