# HaiChatGPT

HaiChatGPT是一个免费的体验版的ChatGPT, 基于OpenAI官方API实现。无需翻墙，流式输出，快速体验ChatGPT。

如果本项目对您有帮助，请右上角给个**star**，谢谢！

已发布页面[ai.ihep.ac.cn](http://ai.ihep.ac.cn)(需所内网或连VPN)，[点此公网](http://47.114.37.111/)(作者个人api_key额度已耗尽，仅展示界面用)。

# 更新日志

+ [2023.03.01] 性能升级！使用Token登录，接入官网版的ChatGPT(原使用API_KEY基于GPT3)
+ [2023.02.17] 官方版保姆级注册教程和临时梯子奉上，[注册教程](docs/reg_tutorial.md)。
+ [2023.02.14] 请求错误时不会崩溃，错误信息会显示在网页界面上。
+ [2023.02.13] 可以设置个人API_KEY了，将OpenAI的[API_KEY](https://platform.openai.com/account/api-keys)粘贴到~/.openai/api_key中并保存即可。
+ [2023.02.11] 添加了Web GUI，可通过python flask_run.py运行。
+ [2023.02.08] 初始版本，可通过命令行运行。


# 网页界面
![hai-gpt-webui](https://zhangzhengde0225.github.io/images/blog/haichatgpt-web-gui.jpg)

部署：
```bash
python flask_run.py --host 0.0.0.0 --port 5000
```
然后访问：http://localhost:5000


# 命令行界面 
![hai chat gpt cli](https://zhangzhengde0225.github.io/images/blog/hai-chat-gpt_cli.png)

使用命令行界面:
```bash
pip install hai-chat-gpt --upgrade # 安装，需python3.6+
HaiChatGPT # 使用命令行运行
```

## 获取Access Token

需使用官方账号登录[ChatGPT](http://ai.com)后，从浏览器的cookies中获取，登录成功后点此处：
[https://chat.openai.com/api/auth/session](https://chat.openai.com/api/auth/session)

## TODO
+ Web GUI，20230211，已完成
+ GPT-3.5，20230301，已完成

## 致谢
该项目基于[OpenAI](www.OpenAI.com)和acheong08的[ChatGPT](https://github.com/acheong08/ChatGPT)项目。


<!-- 一个表格 -->
| 姓名 | 年龄 | 性别 |
| ---- | ---- | ---- |
| 张三 | 18 | 男 |
| 李四 | 19 | 女 |
