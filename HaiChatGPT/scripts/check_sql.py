
"""
用来统计用户数量，每个用户的提问数目和答案等数据。
"""
import pandas as pd
import sqlalchemy

import requests

import numpy as np


if __name__ == '__main__':
    # 统计用户数量，和sso用户
    engine = sqlalchemy.create_engine('mysql://root:123qwe@localhost/user_data')
    df = pd.read_sql("select * from users", engine)
    data_users = df.to_dict(orient='records')

    users_type_local = 0
    users_type_sso = 0
    users_type_ihep = 0
    for user in data_users:
        if user.get('auth_type') == 'local':
            users_type_local += 1
        elif user.get('auth_type') == 'sso':
            users_type_sso += 1
        else:
            users_type_local += 1

        if user.get('name').endswith('@ihep.ac.cn'):
            users_type_ihep += 1

            # raise ValueError(f'Unknown auth_type: {v["auth_type"]}')
    print(f'共计用户数: {len(data_users)}')
    print(f'本地用户数: {users_type_local}')
    print(f'单点登录用户数: {users_type_sso}')
    print(f'ihep用户数: {users_type_ihep}')

    # 统计用户的历史有效问题数
    def check_question(question):
        # 判断是否是有效问题的prompt
        messages = [ 
                    {"role": "user", "content": f"下列的文字是否是一个有效的提问？请在0到10之间打分，并只回复分数：{question}"},
                ]

        res = requests.post('http://192.168.68.22:42901/v1/chat/completions',
        headers={"Authorization": "Bearer iRRkpnBUdsHbYpzSCjdDHawrjTAfvC"},
        json={
                "model":"openai/gpt-3.5-turbo",
                "messages": messages,
                "stream" :True,
                # "max_new_tokens": 2048,
                },
            stream = True,
        )

        answer = ""
        for x in res.iter_content(chunk_size=1000):
            answer = answer + x.decode('utf-8')

        # 删除多余的字符
        answer = answer.split('[DONE]')[0]
        try:
            return int(answer)
        except:
            return 0
        


    df = pd.read_sql("select * from histories", engine)
    data = df.to_dict(orient='records')
    users_history_count = {}
    total_count = 0
    qulity_count = 0

    ihep_count = 0
    ihep_total_count = 0
    ihep_qulity_count = 0
    for user in data:
        if user['user_id'] not in users_history_count.keys():
            users_history_count[user['user_id']] = 0
            if user['username'].endswith('@ihep.ac.cn'):
                ihep_count += 1

        if user['role'] == 'user':
            if len(list(user['content'])) > 5:
                qulity_count += 1
                if user['username'].endswith('@ihep.ac.cn'):
                    ihep_qulity_count += 1
            total_count += 1
            if user['username'].endswith('@ihep.ac.cn'):
                ihep_total_count += 1
            users_history_count[user['user_id']] += 1
        elif user['role'] == 'assistant':
            pass
    # info = dm.misc.dict2info(users_history_count)
    info = ""
    print(f'共计{len(users_history_count)}个用户有{total_count}个问题')
    print(f'共计{qulity_count}个有效问题')
    print(f'共计{ihep_count}个ihep用户提问')
    print(f'ihep用户共计{ihep_total_count}个问题')
    print(f'ihep用户共计{ihep_qulity_count}个有效提问')
          
    # print(f'共计{len(users_history_count)}个用户有{total_count}个历史对话:\n{info}')
    # print(users_history_count)
    # print(total_count)
    
    # 统计用户的问题的长度分布
    df = pd.read_sql("select * from histories", engine)
    # 
    data = df.to_dict(orient='records')
    conntent_len = []
    for user in data:
        if user['role'] == 'user':
            length = len(list(user['content']))
            if length > 5000:
                pass
                # print(user['content'])
            conntent_len.append(len(list(user['content'])))
    conntent_len = np.array(conntent_len)

    bins = [0, 6, 10, 50, 100, 500, 1000, 5000, 10000, 1000000]
    hist = np.histogram(conntent_len, bins=bins)
    hist = np.array(hist)
    print(f'问题的长度分布: {hist}')

    # 统计用户的提问数量分布
    df = pd.read_sql("select * from histories", engine)
    data = df.to_dict(orient='records')
    user_question_count = {}
    total_count = 0
    for user in data:
        if user['role'] == 'user':
            if user['user_id'] not in user_question_count.keys():
                user_question_count[user['user_id']] = 0
            user_question_count[user['user_id']] += 1
    
    for user, value in user_question_count.items():
        if value > 1000:
            username = data_users[user-1]['name']
            print(username, value)
    
    # 找出问题最多的用户
    user_question_count = sorted(user_question_count.items(), key=lambda x: x[1], reverse=True)
    print(user_question_count[:10])

    user_question_count = np.array(list(user_question_count.values()))

    bins = [0, 1, 2, 3, 4, 5, 10, 20, 50, 100,1000,10000,1000000]
    hist = np.histogram(user_question_count, bins=bins)
    hist = np.array(hist) # / np.sum(user_question_count)
    print(f'用户的提问数量分布: {hist}')





    

