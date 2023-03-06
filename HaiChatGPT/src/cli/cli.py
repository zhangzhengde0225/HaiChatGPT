
import sys, os
import damei as dm




def get_input(prompt):
    """
    Multi-line input function
    """
    # Display the prompt
    print(prompt, end="")

    # Initialize an empty list to store the input lines
    lines = []

    # Read lines of input until the user enters an empty line
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    # Join the lines, separated by newlines, and store the result
    user_input = "\n".join(lines)

    # Return the input
    return user_input

def chatbot_commands(chatbot, cmd: str) -> bool:
    """
    Handle chatbot commands
    """
    if cmd == "!help":
        print(
            """
        !help - Display this message
        !rollback - Rollback chat history
        !reset - Reset chat history
        !prompt - Show current prompt
        !save_c <conversation_name> - Save history to a conversation
        !load_c <conversation_name> - Load history from a conversation
        !save_f <file_name> - Save all conversations to a file
        !load_f <file_name> - Load all conversations from a file
        !exit - Quit chat
        """,
        )
    elif cmd == "!exit":
        exit()
    elif cmd == "!rollback":
        chatbot.rollback(1)
    elif cmd == "!reset":
        chatbot.reset()
    elif cmd == "!prompt":
        print(chatbot.prompt.construct_prompt(""))
    elif cmd.startswith("!save_c"):
        chatbot.save_conversation(cmd.split(" ")[1])
    elif cmd.startswith("!load_c"):
        chatbot.load_conversation(cmd.split(" ")[1])
    elif cmd.startswith("!save_f"):
        chatbot.conversations.save(cmd.split(" ")[1])
    elif cmd.startswith("!load_f"):
        chatbot.conversations.load(cmd.split(" ")[1])
    else:
        return False
    return True

def print_head_info():
    print(
        """
    HaiChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
    Repo: github.com/zhangzhengde0225/HaiChatGPT
    """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")
    

def cli_main(chatbot):
    print_head_info()
    # Get API key from command line
    parser = dm.argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        required=False,
        default=None,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream response",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature for response",
    )
    args = parser.parse_args()
    
    while True:
        try:
            prompt = get_input("\nYou:\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        if prompt.startswith("!"):
            if chatbot_commands(chatbot, prompt):
                continue
        if not args.stream:
            response = chatbot.ask(prompt, temperature=args.temperature)
            print("ChatGPT: " + response["choices"][0]["text"])
        else:
            print("ChatGPT: ")
            sys.stdout.flush()
            for response in chatbot.ask_stream(prompt, temperature=args.temperature):
                print(response, end="")
                sys.stdout.flush()
            print()



def cli_main_token(chatbot):
    print_head_info()
    
    while True:
        try:
            prompt = get_input("\nYou:\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        if prompt.startswith("!"):
            if chatbot_commands(chatbot, prompt):
                continue
        # 只有stream
        print("ChatGPT: ")
        # sys.stdout.flush()

        prev_text = ""
        for data in chatbot.ask(prompt):
            # print(data)
            message = data["message"][len(prev_text) :]
            print(message, end="", flush=True)
            prev_text = data["message"]
        print()



def cli_main_35(chatbot, proxy=None):
    """
    Main function
    """
    print_head_info()
    
    # Get API key from command line
    parser = dm.argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        required=True,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature for response",
    )
    parser.add_argument(
        "--no_stream",
        action="store_true",
        help="Disable streaming",
    )
    parser.add_argument(
        "--base_prompt",
        type=str,
        default="You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
        help="Base prompt for chatbot",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=proxy,
        help="Proxy address",
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=1,
        help="Top p for response",
    )
    parser.add_argument(
        "--reply_count",
        type=int,
        default=1,
        help="Number of replies for each prompt",
    )
    parser.add_argument(
        "--enable_internet",
        action="store_true",
        help="Allow ChatGPT to search the internet",
    )
    args = parser.parse_args()
    # Initialize chatbot
    # chatbot = Chatbot(
    #     api_key=args.api_key,
    #     system_prompt=args.base_prompt,
    #     proxy=args.proxy,
    #     temperature=args.temperature,
    #     top_p=args.top_p,
    #     reply_count=args.reply_count,
    # )
    
    # Check if internet is enabled
    if args.enable_internet:
        chatbot.system_prompt = """
        You are ChatGPT, an AI assistant that can access the internet. Internet search results will be sent from the system in JSON format.
        Respond conversationally and cite your sources via a URL at the end of your message.
        """
        chatbot.reset(
            convo_id="search",
            system_prompt='For given prompts, summarize it to fit the style of a search query to a search engine. If the prompt cannot be answered by an internet search, is a standalone statement, is a creative task, is directed at a person, or does not make sense, type "none". DO NOT TRY TO RESPOND CONVERSATIONALLY. DO NOT TALK ABOUT YOURSELF. IF THE PROMPT IS DIRECTED AT YOU, TYPE "none".',
        )
        chatbot.add_to_conversation(
            message="What is the capital of France?",
            role="user",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="Capital of France",
            role="assistant",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="Who are you?",
            role="user",
            convo_id="search",
        )
        chatbot.add_to_conversation(message="none", role="assistant", convo_id="search")
        chatbot.add_to_conversation(
            message="Write an essay about the history of the United States",
            role="user",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="none",
            role="assistant",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="What is the best way to cook a steak?",
            role="user",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="How to cook a steak",
            role="assistant",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="Hello world",
            role="user",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="none",
            role="assistant",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="Who is the current president of the United States?",
            role="user",
            convo_id="search",
        )
        chatbot.add_to_conversation(
            message="United States president",
            role="assistant",
            convo_id="search",
        )

    import re
    from prompt_toolkit import prompt
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory

    def create_session() -> PromptSession:
        return PromptSession(history=InMemoryHistory())


    def create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
        return WordCompleter(words=commands, pattern=re.compile(pattern_str))
    
    def get_input35(session: PromptSession = None, completer: WordCompleter = None) -> str:
        """
        Multiline input function.
        """
        return (
            session.prompt(
                # proxy=proxy,
                completer=completer,
                multiline=True,
                auto_suggest=AutoSuggestFromHistory(),
            )
            if session
            else prompt(multiline=True)
        )



    session = create_session()
    completer = create_completer(
        [
            "!help",
            "!exit",
            "!reset",
            "!rollback",
            "!config",
            "!engine",
            "!temperture",
            "!top_p",
            "!reply_count",
            "!save",
            "!load",
        ],
    )
    # Start chat
    import requests
    import json
    while True:
        print()
        try:
            # print("User: ")
            # prompt = get_input35(session=session, completer=completer)
            prompt = get_input("\nYou:\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        if prompt.startswith("!") and chatbot.handle_commands(prompt):
            continue
        print("ChatGPT: ", flush=True)
        if args.enable_internet:
            query = chatbot.ask(
                f'This is a prompt from a user to a chatbot: "{prompt}". Respond with "none" if it is directed at the chatbot or cannot be answered by an internet search. Otherwise, respond with a possible search query to a search engine. Do not write any additional text. Make it as minimal as possible',
                convo_id="search",
                temperature=0.0,
            ).strip()
            print("Searching for: ", query, "")
            # Get search results
            search_results = (
                '{"results": "No search results"}'
                if query == "none"
                else requests.post(
                    url="https://ddg-api.herokuapp.com/search",
                    json={"query": query, "limit": 3},
                    timeout=10,
                ).text
            )
            print(json.dumps(json.loads(search_results), indent=4))
            chatbot.add_to_conversation(
                f"Search results:{search_results}",
                "system",
                convo_id="default",
            )
            if args.no_stream:
                print(chatbot.ask(prompt, "user", convo_id="default"))
            else:
                for query in chatbot.ask_stream(prompt):
                    print(query, end="", flush=True)
        elif args.no_stream:
            print(chatbot.ask(prompt, "user"))
        else:
            for query in chatbot.ask_stream(prompt):
                print(query, end="", flush=True)
        print()
