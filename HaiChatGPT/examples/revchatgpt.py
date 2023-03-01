from revChatGPT.V1 import Chatbot

chatbot = Chatbot(config={
#   "email": "",
#   "password": "",
  "access_token": "",
})

print("Chatbot: ")
prev_text = ""
for data in chatbot.ask(
    "最快的排序算法是什么，用python实现",
):
    message = data["message"][len(prev_text) :]
    print(message, end="", flush=True)
    prev_text = data["message"]
print()