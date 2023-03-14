
import requests
import time
import multiprocessing as mp
import math
import damei as dm

logger = dm.get_logger('check_network')


def check_network(chatbot, timeout: int = 5):
    """检查网络是否通顺,否则提示使用代理"""
    # logger.info("Checking network...")
    # print("Checking network...", end='')
    
    share_value = mp.Value('i', 0)  # 整形
    api_key = chatbot.api_key
    proxies = chatbot.session.proxies
    p = mp.Process(target=try_request, args=(share_value, api_key, proxies))
    p.start()

    t = time.time()
    while True:
        delta = math.floor(time.time() - t)
        # logger.debug(share_value.value)
        print(f'\rChecking network...{"."*delta} ', end='')
        if share_value.value == 200:  # success
            # 关闭进程
            p.terminate()
            break
        if delta > timeout:
            p.terminate()
            break
        
        time.sleep(1)
    p.join()
    if share_value.value == 200:
        # logger.info("Network is OK.")
        print(" Success.")
        # logger.debug(f"Current engine: {self.engine}\nAvailable Engines:\n" + self.text)
    else:
        print(" Failed.")
        raise ValueError("Can't connect to OpenAI API, try to set a proxy like `--proxy http://127.0.0.1:1086`.")
        

def try_request(share_value, api_key, proxies=None):
    """尝试请求,如果失败则尝试使用代理"""
    # headers = {"Authorization": f"Bearer {api_key}"}
    for i in range(5):
        logger.debug(f"try request {i}")
        reponse = requests.get(
            # "https://api.openai.com/v1/engines",
            "https://www.google.com",
            proxies=proxies,
            # headers=headers,
            timeout=5,
        )
        if reponse.status_code == 200:
            share_value.value = reponse.status_code
            break
        else:
            share_value.value = reponse.status_code
        # return reponse
        time.sleep(1)
    