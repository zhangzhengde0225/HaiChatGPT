# HaiChatGPT

HaiChatGPT是一个免费的体验版的ChatGPT, 基于OpenAI官方API实现。无需翻墙，流式输出，快速体验ChatGPT。

如果本项目对您有帮助，请右上角给个**star**，谢谢！

已发布webui: [ai.ihep.ac.cn](https://ai.ihep.ac.cn).

# 更新日志

+ [2023.03.13] 使用MySQL保存数据
+ [2023.03.01] 性能升级！使用Token登录，接入官网版的ChatGPT(原使用API_KEY基于GPT3)
+ [2023.02.17] 官方版保姆级注册教程和临时梯子奉上，[注册教程](docs/reg_tutorial.md)。
+ [2023.02.14] 请求错误时不会崩溃，错误信息会显示在网页界面上。
+ [2023.02.13] 可以设置个人API_KEY了，将OpenAI的[API_KEY](https://platform.openai.com/account/api-keys)粘贴到~/.openai/api_key中并保存即可。
+ [2023.02.11] 添加了Web GUI，可通过python flask_run.py运行。
+ [2023.02.08] 初始版本，可通过命令行运行。

# MySQL
1. 安装好MySQL，并设置用户和密码
2. 打开MySQL，并创建数据库
```bash
mysql -u username -p
```
```myscql
CREATE DATABASE IF NOT EXISTS mydatabase;
```
3. 在 src/webui/app.py 中加入
```python
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host/mydatabase'
db = SQLAlchemy(app)
```
4. 可以使用 query.filter_by 搜索数据库，例如搜索用户，会话，和信息
```python
user = UserData.query.filter_by(name=user).first()
chat = UserChat.query.filter_by(user_id=user.id, chat=chat_name).first()
messages = UserMessage.query.filter_by(chat_id=chat.id).all()
```
5. flask 中也可以重建数据库
```python
with app.app_context():
    db.drop_all()
    db.create_all()
```

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
