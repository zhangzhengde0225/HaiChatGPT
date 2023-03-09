



class YieldDemo(object):
    def __init__(self) -> None:
        self.flag = None
        pass

    def __call__(self):
        text = 'hello I am a generator'
        self.flag = True
        gen = self.text2stream(text)
        return gen

    def text2stream(self, text):
        """将text转为generator"""
        for i, line in enumerate(text):
            data = text[:i+1]
            data = data.replace("\n", "<|im_br|>")
            yield f'data: {data}'
        self.flag = False


if __name__ == "__main__":
    yy = YieldDemo()
    a = yy()
    print(a)
    for x in a:
        print(x)
    print(yy.flag)
