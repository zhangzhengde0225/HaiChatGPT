
// 获取DOM元素
const loginButton = document.getElementById('login-button');
const logoutButton = document.getElementById('logout-button');
const usernameLabel = document.getElementById('username-label');

user_name = localStorage.getItem('username')
// console.log(user_name); 

if (localStorage.getItem('username') !== null) {
  // 已登录
  loginButton.style.display = 'none';
  logoutButton.style.display = 'inline-block';
  usernameLabel.style.display = 'inline-block';
  usernameLabel.innerText = localStorage.getItem('username');
} else {
  // 未登录
  loginButton.style.display = 'inline-block';
  logoutButton.style.display = 'none';
  usernameLabel.style.display = 'none';
  usernameLabel.innerText = '';
}

// 监听 登录按钮 显示登录对话框
loginButton.addEventListener('click', () => {
    window.location.href = 'login-dialog.html';
  });

// 监听 登出按钮 清除本地存储的用户名
logoutButton.addEventListener('click', function(event) {
  // 阻止
  event.preventDefault();

  username = localStorage.getItem('username');
  // localStorage.removeItem('username'); 
  
  fetch('/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: username
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // 登出成功
      alert(data.message);
      // 清除本地存储的用户名
      // localStorage.setItem('username', null);
      localStorage.removeItem('username');
      // localStorage.removeItem('username');
      // 清除本地Cookie
      // document.cookie = 'session=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
      loginButton.style.display = 'inline-block';
      logoutButton.style.display = 'none';
      usernameLabel.style.display = 'none';
      usernameLabel.innerText = '';
    } else {
      // 登出失败
      alert(data.message);
    }
  })
  .catch(error => {
    console.error(error);
    console.log('error');
  });

  // window.location.href = '/';
});








