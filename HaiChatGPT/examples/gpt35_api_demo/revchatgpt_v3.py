
# api_key = "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"
api_key = "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"

def run():
    from revChatGPT.V3 import Chatbot
    chatbot = Chatbot(
        api_key=api_key,
        proxy="localhost:1086",
        )
    for data in chatbot.ask_stream("Hello world"):
        print(data, end="", flush=True)


def run2():
    import openai
    openai.api_key = api_key
    print(openai.api_key)
    print(openai.Model.list())
    return
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "用python写冒泡排序"},
        ]
    )
    print(response)

if __name__ == "__main__":
    # run()
    run2()
