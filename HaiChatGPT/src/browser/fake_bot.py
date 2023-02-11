
import time


class FakeChatGPT(object):
    def __init__(self) -> None:
       
        self.count = 0
        self.max_qa = 50
        self.qa_pairs = []  # 保存历史的问答对qustion, answer

        # self.query('question1')
        # self.query('question2')
        # self.has_new_pair = False
        # self.new_question = None
        # self.last_question = ''
        # self.last_full_answer = ''

        self.show_history = False

        self.show_last_question = False
        self.show_last_answer = False
        self.last_question = None
        self.last_answer = None
    
    def append_qa(self, text, answer):
        if len(self.qa_pairs) >= self.max_qa:
            self.qa_pairs.pop(0)
        self.qa_pairs.append((text, answer))
        
    def query(self, text):
        answer = f'I am the answer {self.count} for "{text}".'
        self.count += 1
        return answer

    def query_stream(self, text):
        # self.last_question = text
        self.last_answer = ''
        def generator():
            data = f'I am the stream answer {self.count} for "{text}".'
            for x in data:
                yield f'data: {x}\n\n'
                time.sleep(0.05)
                self.last_answer += x
        generator = generator()
        self.count += 1
        # self.new_question = text
        # # self.append_qa(text, answer)
        # self.count += 1
        return generator
