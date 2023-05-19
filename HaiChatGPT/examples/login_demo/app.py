from flask import Flask, render_template, request

import damei as dm


logger = dm.get_logger(__name__)
app = Flask(__name__)
from utils.user_manager import UserManager
user_mgr = UserManager()


# 主页
@app.route('/')
def index():
    logger.info('index')
    return render_template('index.html')

# 登录对话框
@app.route('/login-dialog.html')
def login_dialog():
    return render_template('login-dialog.html')

@app.route('/user-info.html')
def user_info():
    return render_template('user-info.html')

# 处理登录表单提交
@app.route('/login', methods=['POST'])
def login():
    logger.info('login')
    data = request.get_json()
    logger.info(f'request data: {data}')
    username = data.get('username')
    password = data.get('password')
    # 在此处进行验证
    # 如果验证成功，将返回一个JSON响应
    # 如果验证失败，将返回一个错误消息
    is_exist = user_mgr.is_exist(username)
    if is_exist:
        return {'success': False, 'message': 'Username Already Exists.'}
    user_mgr.add_user(username, password)
    return {'success': True, 'username': username}
    

if __name__ == '__main__':
    app.run()
