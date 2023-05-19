

from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_user_data")
def get_user_data():
    user_data = {
        "username": "张三",
        "phone": "13012345678",
        "email": "zhangsan@example.com",
        "type": "免费用户",
        "limit": 10,
        "group": "无",
        "group_members": "无",
    }
    return jsonify(user_data)

if __name__ == "__main__":
    app.run(debug=True)
