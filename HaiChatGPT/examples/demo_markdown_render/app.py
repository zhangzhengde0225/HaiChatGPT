from flask import Flask, render_template, Response, stream_with_context
from markdown import markdown
# import markdown
# from markdown.extensions.codehilite import CodeHiliteExtension

import time

app = Flask(__name__)
# md = markdown.Markdown(extensions=[
#     'markdown.extensions.extra', 'markdown.extensions.codehilite',
#     CodeHiliteExtension()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream_route():
    print('stream_route')
    def generate():
        while True:
            markdown_text = get_markdown_text()  # 获取 Markdown 文本
            # markdown_text = markdown_text.replace('\n', '<|im_br|>')
            # html_text = markdown(markdown_text)  # 将 Markdown 转换为 HTML
            html_text = markdown_text
            # html_text = md.convert(markdown_text)
            # print([html_text])
            html_text = html_text.replace('\n', '<|im_br|>')
            print([html_text])
            # html_text = html_text.split()
            for i in range(len(html_text)):
                # yield html_text[i]
                yield f'data: {html_text[:i+1]}\n\n'
                time.sleep(0.0001)  # 等待一段时间，模拟实时更新
            yield '\n\n'  # 插入一个空行，以便 EventSource 解析器正确处理换行符
            time.sleep(20)  # 等待一段时间，模拟实时更新
    # 创建数据流响应
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


def get_markdown_text():
    # answer = f'# I am the answer {self.count} for "{text}".\n\n'
    answer = "冒泡排序是一种简单的排序算法，其基本思想是重复遍历要排序的数组，每次比较相邻的两个元素，如果它们的顺序错误就交换它们的位置。经过一轮遍历之后，最大的元素就被排在了数组的末尾，接着对剩余的元 素进行相同的操作，直到整个数组都被排序为止。\n\n以下是用 Python 编写的冒泡排序的实现：\n\n```python\nimport os\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n```\n\n这段代码中，`bubble_sort` 函数接收一个数组 `arr` 作为参数，使用两层循环遍历数组，并在内层循环中比较相邻的元 素，如果顺序不正确就交换它们的位置。外层循环控制整个排序的次数，因为每次遍历都会将当前最大的元素移动到数组的末尾，所以每次内层循环都可以少比较一次元素。"
    answer += "\n```\nint main() {\n    return 0;\n}\n```\n\n"
    return answer

if __name__ == '__main__':
    app.run(debug=True)
