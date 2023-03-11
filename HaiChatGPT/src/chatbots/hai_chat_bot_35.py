"""
HaiChatBot via OpenAI API_KEY, based on GPT-3
"""

import os
import copy
import traceback

from ...repos.ChatGPT.src.revChatGPT.V3 import Chatbot

import damei as dm
import time

logger = dm.get_logger('hai_chat_bot_35')

class HChatBot(Chatbot):

    def __init__(self, 
                api_key: str,
                engine: str = None,
                proxy: str = None,
                max_tokens: int = 3000,
                temperature: float = 0.5,
                top_p: float = 1.0,
                reply_count: int = 1,
                system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
                **kwargs,
                ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        super().__init__(api_key, engine, proxy, max_tokens, temperature, top_p, reply_count, system_prompt)
        self.temperature = temperature

        # 为对话增加的设置
        self.max_history = kwargs.pop('max_history', 10)
        self.show_history = False

        # 定义一个缓冲区，用于存储stream的结果
        self._stream_buffer = None

        self.error_handler = ErrorHandler()

    @property
    def stream_buffer(self):
        return self._stream_buffer
    
    def truncate_convo_and_save(self, convo_id: str = 'default', **kwargs):
        """截断对话，只保留最近的max_history条"""
        self.max_history = kwargs.pop('max_history', self.max_history)
        one_convo = self.conversation.get(convo_id, None)
        if one_convo is None:
            return
        username = kwargs.pop('username', None)
        user_mgr = kwargs.pop('user_mgr', None)
        # logger.debug(f'save username: {username}, user_mgr: {user_mgr}')
        while True:
            if len(one_convo) <= self.max_history + 1:
                break
            one_entry = one_convo.pop(1)  # is a dict
            if user_mgr is not None:
                user_mgr.save_history(username, convo_id, one_entry)
    
    def get_history(self, convo_id: str = 'default', **kwargs):
        one_convo = self.conversation.get(convo_id, None)  # 读出来是一个list
        self.truncate_convo_and_save(convo_id, **kwargs)  # 根据max_history截断对话
        if one_convo is None:
            return None
        history = []
        tmp = [None, None]  # 用于存储user和assistant的内容
        # logger.debug(f'one_convo: {one_convo}')
        for i, data in enumerate(one_convo):
            role = data['role']
            content = data['content']
            # logger.debug(f'role: {role}, content: {content}')
            if role == 'system':
                continue
            if role == 'user':  # 遍历到user，找到对应的assistant
                """每个user找到对应的assistant，然后将user和assistant的内容拼接起来"""
                try:
                    next_data = one_convo[i+1]
                except:
                    tmp[0] = content  # user的content，即问题
                    tmp[1] = 'Answer not saved. without nextdata'
                    history.append(copy.deepcopy(tmp))
                    tmp = [None, None]
                    continue
                next_role = next_data['role']
                if next_role == 'user':
                    tmp[0] = content
                    tmp[1] = 'Answer not saved. next role is user'
                    history.append(copy.deepcopy(tmp))
                    tmp = [None, None]
                    continue
                else:
                    tmp[0] = content
                    tmp[1] = next_data['content']
                    history.append(copy.deepcopy(tmp))
                    tmp = [None, None]
                    continue
            else:  # 便利到assistant的内容，直接跳过
                continue
        if history == []:
            return None
        # 需要把所有的内容中的\n替换成<|im_br|>
        for i, (q, a) in enumerate(history):
            q = q.replace("\n", "<|im_br|>")
            a = a.replace("\n", "<|im_br|>")
            history[i] = (q, a)
        # 再把所有的内容拼接起来，q和a用<|im_sep|>分割，两个对话之间用bbbr分割
        history = '<|im_bbbr|>'.join([f'{q}<|im_sep|>{a}' for q, a in history])
        return history

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def set_engine(self, engine: str) -> None:
        self.engine = engine

    def set_temperature(self, temperature: float) -> None:
        self.temperature = temperature

    def _query_stream(self, query, **kwargs):

        ret = self.ask_stream(
            prompt=query,
            role="user",
            convo_id='default',
            **kwargs,
            )
        
        self.last_answer = ''
        
        def convert_generator():
            try:
                text = ''
                for content in ret:
                    text += content
                    b = text.replace("\n", "<|im_br|>")
                    yield f'data: {b}\n\n'
                    # logger.debug(f'content: {content}')
                self.last_answer = text
                self._stream_buffer = None
            except Exception as e:
                error_info = self.error_handler.handle(e)
                logger.error(error_info)
                self._stream_buffer = self.text2stream(error_info)
        return convert_generator()
        
        
    def query_stream(self, query, **kwargs):
        """包含错误处理的query_stream"""
        try:
            if query.startswith('sysc') or query.startswith('SYSC'):
                # logger.debug(f'command: {query}')
                return self._handle_commands(query, **kwargs)
            else:
                # raise KeyError('Rate lim one_convot reachedssss')
                return self._query_stream(query, **kwargs)
        except Exception as e:
            error_info = self.error_handler.handle(e)
            return self.text2stream(error_info)

    
    def _handle_commands(self, command, convo_id='default', **kwargs):

        if command in ['sysc', 'SYSC', 'sysc ', 'SYSC ']:
            info = self.get_help()
            return self.text2stream(info)
        
        if command.startswith('sysc') or command.startswith('SYSC'):
            command = command[4::]
        
        if command.startswith(' ') or command.startswith(':'):
            command = command[1::]
        
        command, *args = command.split()
        if command in ['help', '帮助']:
            info = self.get_help()
            return self.text2stream(info)
        elif command in ['reset', '重置']:
            self.reset(convo_id=convo_id)
            return self.t2s("对话已重置")
        elif command in ['config', '配置']:
            return self.t2s(self.get_config())
        elif command in ['rollback', '回滚']:
            self.rollback(int(args[0]), convo_id=convo_id)
            info = f"Rolled back by {args[0]} messages"
            return self.t2s(info)
        elif command in ['save', '保存']:
            if is_saved := self.save(*args):
                convo_ids = args[1:] or self.conversation.keys()
                info = f"Saved conversation(s) {convo_ids} to {args[0]}"
            else:
                info = "Failed to save conversation(s)"
            return self.t2s(info)
        elif command in ['load', '加载']:
            if is_loaded := self.load(*args):
                convo_ids = args[1:] or self.conversation.keys()
                info = f"Loaded conversation(s) {convo_ids} from {args[0]}"
            else:
                info = "Failed to load conversation(s)"
            return self.t2s(info)
        elif command in ['temperature', '温度']:
            self.temperature = float(args[0])
            self.set_user_cookie(temperature=float(args[0]), **kwargs)
            info = f"温度已经设置为{args[0]}，输入sysc config查看"
            return self.t2s(info)
        elif command in ['engine', '引擎']:  # TODO: 保存用户的上次设置
            self.engine = args[0]
            self.set_user_cookie(engine=args[0], **kwargs)
            info = f"引擎已经设置为{args[0]}，输入sysc config查看"
            return self.t2s(info)
        elif command in ['api_key', 'api密钥']:
            self.api_key = args[0]
            self.set_user_cookie(api_key=args[0], **kwargs)
            secrete_api_key = f'{args[0][:4]}{"*"*(len(args[0])-8)}{args[0][-4:]}'
            info = f"API密钥已经设置为{secrete_api_key}，输入sysc config查看"
            return self.t2s(info)
        elif command in ['more', '更多']:
            info = self.get_more()
            return self.t2s(info)
        else:
            raise ValueError(f'未知的命令: `{command}`，输入`sysc help`查看帮助')
    
    def set_user_cookie(self, **kwargs):
        user_mgr = kwargs.pop('user_mgr', None)
        if user_mgr is None:
            return
        user_name = kwargs.pop('user_name', None)
        if user_name is None:
            raise ValueError('Cannot save user cookie when you are not logged in.')
        user_mgr.write_cookie(user_name, **kwargs)  # 保存用户的设置
        
    
    def t2s(self, text, time_interval=0.001):
        return self.text2stream(text, time_interval=time_interval)
            
    def text2stream(self, text, time_interval=0.001):
        """将text转为generator"""
        for i, line in enumerate(text):
            data = text[:i+1]
            data = data.replace("\n", "<|im_br|>")
            yield f'data: {data}\n\n'
            time.sleep(time_interval)
        yield f'data: <|im_end|>\n\n'
        self._stream_buffer = None  # 这段代码在generator被遍历后才会运行，清空缓冲区

    def get_help(self):
        help_info = f"## 帮助\n\n"
        help_info += f"### 系统命令：\n\n"
        help_info += f"+ 1. 输入`sysc help`查看此帮助\n\n"
        help_info += f"+ 2. 输入`sysc config`查看配置\n\n"
        help_info += f"+ 3. 输入`sysc reset`重置对话\n\n"
        help_info += f"+ 4. 输入`sysc rollback 2`回滚2条消息\n\n"
        # help_info += f"+ 5. 输入`sysc save filename`保存对话到filename\n\n"
        # help_info += f"+ 6. 输入`sysc load filename`从filename加载对话\n\n"
        help_info += f"+ 5. 输入`sysc temperature 0.5`设置温度为0.5，温度越高回答越随机\n\n"
        # help_info += f"+ 8. 输入`sysc engine gpt-3.5-turbo`设置引擎为gpt-3.5-turbo\n\n"
        
        
        help_info += f"+ 6. 输入`sysc api_key xxx`设置API密钥为xxx\n\n"
        help_info += f"+ 7. 输入`sysc more`查看更多\n\n"

        help_info += f"### Prompt示例：\n\n"
        help_info += f"+ 1. 请用python写一段快速排序代码\n\n"
        help_info += f"+ 2. 你作为一个python专家回答问题，回答尽可能简洁，不需要解释，除非我询问你。第一个问题是：写一段快速排序代码\n\n"
        
        return help_info
    
    def get_more(self):
        info = f"### 联系我们：\n\n"
        info += f"+ 1. 加入wx交流群请添加：**AI4HEP**\n\n"
        info += f"+ 2. 报告错误请邮件：**zdzhang@ihep.ac.cn**\n\n"
        info += f"+ 3. 开源主页[github.com/zhangzhengde0225/HaiChatGPT](https://github.com/zhangzhengde0225/HaiChatGPT)\n\n"
        info += f"#### 系统指令为什么是sysc？\n\n"
        info += f"致敬[刀剑神域UnderWorld](https://baike.baidu.com/item/Under%20World/16017110?fr=aladdin)，"
        info += f"表示人造世界里神圣术指令的开头：`System Call`\n\n"
        return info

    def get_config(self, convo_id='default'):
        api_key = f'{self.api_key[:4]}****{self.api_key[-4:]}'
        config = "HaiChatGPT Configuration:\n"
        config += f"""
    Messages:         {len(self.conversation[convo_id])} / {self.max_tokens}
    Engine:           {self.engine}
    API_Key:          {api_key}
    Temperature:      {self.temperature}
    Top_p:            {self.top_p}
    Reply_count:      {self.reply_count}
    System_prompt:    {self.system_prompt}
    Max_tokens:       {self.max_tokens}
                        """
    
        return config
        

class ErrorHandler:
    
    """
    error类型：
    openai.error.RateLimitError， 点击速率太快

    """
    def handle(self, e):
        

        error_info = f'{type(e)}: {e}'
        error_info = self.convert_error(e)
        logger.error(f'{error_info}\n {traceback.format_exc()}')

        return error_info

    def convert_error(self, e):
        if 'Rate limit reached' in str(e):
            error_info = f'{type(e)}共用请求速率达到上限，休息一下再试试。\
                或者通过`sysc`设置使用自己的`API-KEY`。'
        else:
            error_info = f'{type(e)}: {e}'
        return error_info
    

    


    
        
        





