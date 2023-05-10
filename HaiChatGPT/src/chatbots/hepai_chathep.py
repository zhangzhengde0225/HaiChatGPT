import os, sys
import hai
import tiktoken
import dataclasses

from ...repos.ChatGPT.src.revChatGPT.V3 import Chatbot
ENCODER = tiktoken.get_encoding("gpt2")

Engine2Model = {
    "gpt-3.5-turbo-0301": 'hepai/gpt-3.5-turbo',
    "chathep-0503": "hepai/chathep-20230503",
    "chatbep-0509": "hepai/chathep-20230509"
}

class ChatHEP(Chatbot):
    def __init__(self, api_key, system_prompt=None, **kwargs):
        super().__init__(api_key, system_prompt=system_prompt, **kwargs)
        models = hai.Model.list()  # 列出可用模型
        print(models)
        self.models = ['hepai/chathep-20230503', 'hepai/gpt-3.5-turbo']
        self._language = kwargs.get('language', 'en')
        # self.system_prompt = system_prompt if system_prompt is not None else "You are ChatGPT, answering questions conversationally"
        self.system_prompt = system_prompt
        print(f'system_prompt: {self.system_prompt}')
        pass

    def engine2model(self, engine):
        if 'chathep' in engine:
            # like "chathep-0503" → "hepai/chathep-20230503"
            return f'hepai/{engine.split("-")[0]}-2023{engine.split("-")[1]}'
        else:
            return "hepai/gpt-3.5-turbo"

    @property
    def prompt_lang(self):
        if self._language == 'zh':
            return '用中文输出'
        elif self._language == 'en':
            return 'output in English'
        else:
            raise ValueError(f'language: {self._language} is not supported')
    
    def __truncate_conversation(self, convo_id: str = "default") -> None:
        """
        Truncate the conversation
        """
        while True:
            full_conversation = "".join(
                message["role"] + ": " + message["content"] + "\n"
                for message in self.conversation[convo_id]
            )
            if (
                len(ENCODER.encode(full_conversation)) > self.max_tokens
                and len(self.conversation[convo_id]) > 1
            ):
                # Don't remove the first message
                self.conversation[convo_id].pop(1)
            else:
                break
        
    def ask_stream(self, prompt: str, role: str = "user", convo_id: str = "default", **kwargs) -> str:
        # Make conversation if it doesn't exist
        if convo_id not in self.conversation:  # 重置会话，只保留role为system的会话
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
        
        ### zzd: 读取和更新system_prompt
        chathep_syspromt = "You are ChatHEP, answering questions conversationally, think step by step."
        # print('engine xx', self.engine)
        default_system_prompt = chathep_syspromt if 'chathep' in self.engine else self.system_prompt
        system_prompt = kwargs.get("system_prompt", default_system_prompt)
        if hasattr(self, "tmp_sys_prompt"):
            if self.tmp_sys_prompt != None:
                system_prompt = self.tmp_sys_prompt
                # self.tmp_sys_prompt = None
        current_prompt = self.conversation[convo_id][0]["content"]
        if current_prompt != system_prompt:
            self.conversation[convo_id][0]["content"] = system_prompt
        ### zzd end
        
        self.add_to_conversation(prompt, "user", convo_id=convo_id)  # 添加用户输入到会话
        self.__truncate_conversation(convo_id=convo_id)  # 根据max_tokens截断会话
        # print(self.conversation[convo_id])
        
        model = self.engine2model(self.engine)
        api_key = kwargs.get("api_key", self.api_key)
        data = {
            "model": model,
            "messages": self.conversation[convo_id],
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": True,
            "timeout": 60,
            # "user": role,
        }
        
        response = self.session.post(
            "https://chat.ihep.ac.cn/v1/chat/completions",
            proxies=self.session.proxies,
            headers={"Authorization": f"Bearer {api_key}"},
            json=data,
            stream=True,
        )
        if response.status_code != 200:
            raise KeyError(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        full_response = ""
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if not chunk:
                continue
            chunk = chunk.decode("utf-8")
            if chunk == "[DONE]":
                break
            full_response += chunk
            yield chunk
        response_role = "assistant"
        self.add_to_conversation(full_response, response_role, convo_id=convo_id)


    def __call__(self, prompt, sys_prompt=None, **kwargs):
        try:
            return self.__call__2(prompt, sys_prompt=sys_prompt, **kwargs)
        except Exception as e:
            print(f'Chat ERROR: {e}')
            return self.__call__(prompt, sys_prompt=sys_prompt, **kwargs)

    def __call__2(self, prompt, sys_prompt=None, **kwargs):
        need_print = kwargs.get('print', True)
        # prompt = "Hello!"
        system_prompt = self.system_prompt if sys_prompt is None else sys_prompt
        api_key = 'iRRkpnBUdsHbYpzSCjdDHawrjTAfvC'  # 这个是hepai的api_key

        result = hai.LLM.chat(
                model=self.models[0],
                api_key=api_key,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
                    ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
                ],
                stream=True,
            )
        # result是一个流式数据生成器，需要遍历获取全部结果
        full_result = self.parse_output(result)
        return full_result
    
    def parse_output(self, result, need_print=True):
        full_result = ""
        for i in result:
            full_result += i
            if need_print:
                sys.stdout.write(i)
                sys.stdout.flush()
        if need_print:
            print()
        return full_result

    def parse_output2(self, output_stream):
        pre = 0
        for outputs in output_stream:
            outputs = outputs.strip().split(" ")
            now = len(outputs) - 1
            if now > pre:
                print(" ".join(outputs[pre:now]), end=" ", flush=True)
                pre = now
        print(" ".join(outputs[pre:]), flush=True)
        return " ".join(outputs)
    
    def cal_tokens(self, text, language=None):
        """大约一个汉字占2个token，一个英文单词占1.333个token"""
        lang = language if language is not None else self._language
        if lang == 'zh':
            return len(text) * 2
        elif lang == 'en':
            return len(text) * 1.333
        else:
            raise ValueError(f'language: {lang} is not supported')
        

if __name__ == '__main__':
    chat = ChatHEP()
    chat('who are you?')
    chat('你是谁？')