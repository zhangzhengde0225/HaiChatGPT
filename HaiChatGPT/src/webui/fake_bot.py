
import time
import damei as dm

logger = dm.get_logger('fake_bot')

class FakeChatGPT(object):
    def __init__(self, **kwargs) -> None:
       
        self.count = 0
        self.max_qa = kwargs.pop('max_qa', 5)
        self.qa_pairs = []  # 保存历史的问答对qustion, answer

        self.show_history = False

        self.show_last_question = False
        self.show_last_answer = False  # its a flag, 
        self.last_question = None
        self.last_answer = None

        self._stream_buffer = None

        print('FakeChatGPT init', 'max_qa:', self.max_qa)  

    @property
    def stream_buffer(self):
        return self._stream_buffer 
    
    def append_qa(self, text, answer):
        if len(self.qa_pairs) >= self.max_qa:
            self.qa_pairs.pop(0)
        self.qa_pairs.append((text, answer))

    def get_answer(self, text):
        answer = f'### 这里是FakeBot的回复：\nQuestion: {text} count: {self.count}.\n\n'
        answer += self.answer_demo_code()

        return answer
    
    def answer_demo_code(self):
        
        answer = f'示例回答支持代码、表格、公式.\n\n'
        answer += "#### 代码：\n\n冒泡排序是一种简单的排序算法，其基本思想是重复遍历要排序的数组，每次比较相邻的两个元素，如果它们的顺序错误就交换它们的位置。经过一轮遍历之后，最大的元素就被排在了数组的末尾，接着对剩余的元 素进行相同的操作，直到整个数组都被排序为止。\n\n以下是用 Python 编写的冒泡排序的实现：\n\n```python\nimport os\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n```\n\n这段代码中，`bubble_sort` 函数接收一个数组 `arr` 作为参数，使用两层循环遍历数组，并在内层循环中比较相邻的元 素，如果顺序不正确就交换它们的位置。外层循环控制整个排序的次数，因为每次遍历都会将当前最大的元素移动到数组的末尾，所以每次内层循环都可以少比较一次元素。\n"
        table = "| 姓名 | 年龄 | 性别 |\n| ---- | ---- | ---- |\n| 张三 | 18 | 男 |\n| 李四 | 19 | 女 |"
        answer += f'#### 表格：\n\n{table}\n\n'

        answer += f"#### 公式：\n\n{self.answer_formulas()}\n\n"
        
        return answer
    
    def answer_formulas(self):
        text = "薛定谔方程是描述量子力学中粒子行为的基本方程之一。它的数学形式如下：\n\niℏ∂ψ/∂t = Ĥψ\n\n其中，i代表虚数单位，ℏ代表约化普朗克常数，ψ是波函数，t是时间，Ĥ 是哈密顿算符。\n\n这个方程的意义是，波函数的时间导数与哈密顿算符作用于波函数的结果成比例。波函数描述了粒子在不同时间的可能位置和状态，而哈密顿算符则描述了粒子在某个给定 状态下的能量和动量。\n\n这个方程非常重要，因为它能够精确描述微观世界中粒子的行为，如原子和分子的行为以及光和其他辐射的行为。"
        return text

    def query(self, text):
        return self.get_answer(text)

    def query_stream(self, text):
        self.last_answer = ''
        logger.debug(f'query_stream: {text}')
        text = self.get_answer(text)
        self.count += 1
        return self.text2stream(text)
        
    def text2stream(self, text, time_interval=0.005):
        """将text转为generator"""
        for i, line in enumerate(text):
            data = text[:i+1]
            data = data.replace("\n", "<|im_br|>")
            yield f'data: {data}\n\n'
            time.sleep(time_interval)
        yield f'data: <|im_end|>\n\n'
        # print('Set stream_buffer to None.')
        logger.debug('Set stream_buffer to None.')
        self._stream_buffer = None  # 这段代码在generator被遍历后才会运行，清空缓冲区
    
    def ask(self, text):
        answer = self.get_answer(text)
        for i, x in enumerate(answer):
            time.sleep(0.01)
            message = answer[:i+1]
            yield {
                "message": message,
                "conversation_id": "fake_cid_01",
                "parent_id": "fake_pid_01",
                "model": "fake_model_01",
            }
