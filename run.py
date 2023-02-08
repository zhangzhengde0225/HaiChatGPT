
def run1():
    from HaiChatGPT import Chat, Options

    options = Options()

    # [New] Pass Moderation. https://github.com/rawandahmad698/PyChatGPT/discussions/103
    # options.pass_moderation = False

    # [New] Enable, Disable logs
    options.log = True

    # Track conversation
    options.track = True 

    # Use a proxy
    # options.proxies = 'http://localhost:8080'
    options.proxies = 'http://47.114.37.111:429'

    # Optionally, you can pass a file path to save the conversation
    # They're created if they don't exist

    # options.chat_log = "chat_log.txt"
    # options.id_log = "id_log.txt"

    # Create a Chat object
    email = 'zhangzhengde0225@gmail.com'
    password = '19930429Mz_'
    # password = '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'
    # chat = Chat(email="email", password="password", options=options)
    chat = Chat(email=email, password=password, options=options)

    answer = chat.ask("How are you?")
    print(answer)


def run2():
    
    from HaiChatGPT import tt
    # tt.run()
    print(tt.response)



if __name__ == '__main__':
    # run1()
    run2()
