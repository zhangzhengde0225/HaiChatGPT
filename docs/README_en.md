
# HaiChatGPT

This project is a ChatGPT GUI based on Hai GUI Framework ([HaiGF](https://code.ihep.ac.cn/zdzhang/hai-gui-framework)).


## Quickstart

```bash
pip install hai-chat-gpt --upgrade  # install

HaiChatGPT  # run with command line
```

#### Command Line Interface:

![hai-chat-gpt-cli](https://zhangzhengde0225.github.io/images/blog/hai-chat-gpt_cli.png)

#### Web GUI:

![hai-chat-gpt-webui](https://zhangzhengde0225.github.io/images/blog/haichatgpt-web-gui.jpg)


## Features

+ Use OpenAI's official interface, fast and no need to use VPN.
+ Stream output, better chat experience.

## Notes

+ The current version is a **trial version**, using the same author's `api_key`.
+ You can get your own `api_key` via [OpenAI](www.openai.com) and set it to environment variable **`OPENAI_API_KEY`**. For example:
    
    ```bash
    export OPENAI_APT_KEY = "sk-xxxxxxxxxxxxxxxxxx"  # on linux
    ```

## TODO

+ Web GUI, 20230211, done
+ GPT-3.5



## Acknowledgement

The project is based on  [OpenAI](www.openai.com) and acheong08's [ChatGPT](https://github.com/acheong08/ChatGPT) project.




