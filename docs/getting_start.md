
## Web UI
部署：
```bash
python flask_run.py --host 0.0.0.0 --port 5000
```
然后访问：http://localhost:5000


## CLI
使用命令行界面:
```bash
pip install hai-chat-gpt --upgrade # 安装，需python3.6+
HaiChatGPT # 使用命令行运行
```

## 关于Access Token

需使用官方账号登录[ChatGPT](http://ai.com)后，从浏览器的cookies中获取，登录成功后点此处：
[https://chat.openai.com/api/auth/session](https://chat.openai.com/api/auth/session)

可以保存多个Access Token到`~/.HaiChatGPT/config.json`中。

## 关于API_KEY

您可以通过[OpenAI](www.OpenAI.com)获取自己的`api_key`, 也可将多个API_KEY保存到`~/.HaiChatGPT/config.json`中。

