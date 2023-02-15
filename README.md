# HaiChatGPT

HaiChatGPT是一个免费的体验版的ChatGPT, 基于OpenAI官方API实现。无需翻墙，快速体验GPT-3的聊天功能。

如果本项目对您有帮助，请右上角给个**star**，谢谢！

## 功能
+ 快速且无需使用VPN。
+ 流输出，更好的聊天体验。

## 更新日志

+ 2021.02.14 添加了错误处理，错误信息会显示在网页界面上，而不会导致程序崩溃。
+ 2023.02.13 个人API可以可设置在~/.openai/api_key中，或者环境变量`OPENAI_API_KEY`中。


## 网页界面
![hai-gpt-webui](https://zhangzhengde0225.github.io/images/blog/haichatgpt-web-gui.jpg)

部署：
```bash
python flask_run.py --host 0.0.0.0 --port 5000
```
然后访问：http://localhost:5000


## 命令行界面 
![hai chat gpt cli](https://zhangzhengde0225.github.io/images/blog/hai-chat-gpt_cli.png)

使用命令界面:
```bash
pip install hai-chat-gpt --upgrade # 安装，需python3.6+
HaiChatGPT # 使用命令行运行
```


## 注意
+ 当前版本是**试用版**，使用同一作者的“api_key”，悠着点用 [/手动狗头]。
+ 您可以通过[OpenAI](www.OpenAI.com)获取自己的`api_key`，并将其设置为环境变量**`OpenAI_api_key`**。例如：
    ```bash
    export OPENAI_APT_KEY="sk-xxxxxxxxxxxxxx"  # on lunix
    ```
## TODO
+ Web GUI，20230211，已完成
+ GPT-3.5
+ 可以反馈使用体验，以便改进

## 致谢
该项目基于[OpenAI](www.OpenAI.com)和acheong08的[ChatGPT](https://github.com/acheong08/ChatGPT)项目。