import time

class RequestLimiter:
    """
    请求限制器
    参数：limit_rate: 限制的请求次数, 默认60次/分钟
    参数：unit: 时间单位，支持minute和second，默认minute
    """
    def __init__(self, limit_rate=60, unit='minute'):
        self.timestamp_list = []
        self.limite_rate = limit_rate
        self.unit = unit
        self.minuend = self.limite_rate if unit == 'minute' else 1

        self.limite_desc = f'{self.minuend}次/{self.unit}'

    def is_limited(self):
        timestamp = time.time()
        self.timestamp_list.append(timestamp)

        # 保留1分钟内的时间戳
        self.timestamp_list = [t for t in self.timestamp_list if t >= timestamp - self.minuend]

        # 如果时间戳数量超过60，则限制请求
        if len(self.timestamp_list) > self.limite_rate:
            overload = f'速率限制为{self.limite_desc}, 但达到了{len(self.timestamp_list)}次每{self.unit}'
            return True, overload
        else:
            return False, ''
