


class HaiChatGPT(object):

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.args = None


    @staticmethod
    def run_cli():
        """Run the command line interface."""
        # from ..apis import cli_main
        from .cli.cli import cli_main, cli_main_v1

        cli_main()
        # cli_main_v1()

    
    @staticmethod
    def run_gui():
        """Run the GUI interface."""
        from ..apis import gui_main
        gui_main()

