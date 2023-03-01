
import time


class FakeChatGPT(object):
    def __init__(self, **kwargs) -> None:
       
        self.count = 0
        self.max_qa = kwargs.pop('max_qa', 5)
        self.qa_pairs = []  # 保存历史的问答对qustion, answer

        self.show_history = False

        self.show_last_question = False
        self.show_last_answer = False
        self.last_question = None
        self.last_answer = None

        print('FakeChatGPT init', self.max_qa)   
    
    def append_qa(self, text, answer):
        if len(self.qa_pairs) >= self.max_qa:
            self.qa_pairs.pop(0)
        self.qa_pairs.append((text, answer))

    def get_answer(self, text):
        answer = f'I am the answer {self.count} for "{text}".'
        code_block = f'\n```import time\ntime.sleep(5)\nprint("Hello World!")```'
        answer += code_block
        answer += '\nNote: This is a fake answer.'

        return answer


    def query(self, text):
        self.count += 1
        return self.get_answer(text)

    def query_stream(self, text):
        # self.last_question = text
        self.last_answer = ''
        def generator():
            # data = f'I am the stream answer {self.count} for "{text}".'
            data = self.get_answer(text)
            for x in data:
                yield f'data: {x}\n\n'
                time.sleep(0.02)
                self.last_answer += x
        generator = generator()
        self.count += 1
        # self.new_question = text
        # # self.append_qa(text, answer)
        # self.count += 1
        return generator
