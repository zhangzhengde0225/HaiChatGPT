// 获取DOM元素
const loginButton = document.getElementById('login-button');
const logoutButton = document.getElementById('logout-button');
const usernameLabel = document.getElementById('username-label');


// 显示登录对话框
loginButton.addEventListener('click', () => {
    window.location.href = 'login-dialog.html';
  });

