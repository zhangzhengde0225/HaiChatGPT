
const username_label = document.getElementById('username-label');

console.log('main.js loaded')

window.onload = function() {
    console.log('window.onload')

    // 从服务器获取当前用户
    fetch('/get_username', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 获取当前用户成功
            const username = data.username;
            // localStorage.setItem('username', username);
            // alert(`登录成功，欢迎您，${username}！`);
            console.log('欢迎回来', username);
            // 如果用户为public或者Null, 则显示登录按钮
            local_user = localStorage.getItem('username');
            if (username == 'public' || username == null) {
                localStorage.setItem('username', null);
            } else if (username !== local_user) {
                // alert(`本地用户${local_user}切换为服务器用户${username}！`);
                // console.log(`本地用户${local_user}切换为服务器用户${username}！`)
                localStorage.setItem('username', username);
            } else {
                // console.log(`本地用户${local_user}与服务器用户${username}一致！`)
            };
            username_label.innerText = username;
            show_login_by_local_storage();
        } else {
            // 获取当前用户失败，显示错误消息
            const message = data.message;
            alert(message);
        }
    }
    )
    .catch(error => {
        console.error(error);
    }
    );

}

