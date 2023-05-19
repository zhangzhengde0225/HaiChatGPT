// 获取DOM元素
// const loginButton = document.getElementById('login-button');
const username = document.getElementById('username');
const loginForm = document.getElementById('login-form');


console.log('login.js loaded');
console.log('username: ', username);
console.log('loginForm: ', loginForm);


// 处理登录表单提交事件
loginForm.addEventListener('submit', (event) => {
  event.preventDefault(); // 阻止表单提交
  console.log(event)
  const usernameValue = event.target.elements.username.value;
  const passwordValue = event.target.elements.password.value;
  // 在此处将用户名和密码发送给后台进行验证
  // 使用fetch API发送POST请求
  // console.log('usernameValue: ', usernameValue);
  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: usernameValue,
      password: passwordValue
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // 登录成功
      const username = data.username;
      // 提示登录成功
      // alert(`登录成功，欢迎您，${username}！`);
      document.getElementById('username').innerText = username;
      document.getElementById('username-label').style.display = 'inline-block';
      document.getElementById('login-button').style.display = 'none';
      document.getElementById('logout-button').style.display = 'inline-block';
    } else {
      // 登录失败，显示错误消息
      const message = data.message;
      alert(message);
    }
  })
  .catch(error => {
    console.error(error);
  });

  // 如果验证成功，将显示已登录的用户名和“Logout”按钮
  username.innerText = usernameValue;
  usernameLabel.style.display = 'inline-block';
  loginButton.style.display = 'none';
  logoutButton.style.display = 'inline-block';
});

// 显示注册表单
registerButton.addEventListener('click', () => {
  loginForm.style.display = 'none';
  registerForm.style.display = 'block';
});

// 处理发送验证码按钮点击事件
sendCodeButton.addEventListener('click', () => {
  const phoneValue = document.getElementById('phone').value;
  // 在此处发送验证码
});

// 处理注册表单提交事件
registerForm.addEventListener('register', (event) => {
  event.preventDefault(); // 阻止表单提交
  const nameValue = event.target.elements.name.value;
  const emailValue = event.target.elements.email.value;
  const phoneValue = event.target.elements.phone.value;
  const codeValue = event.target.elements.code.value;
  // 在此处处理注册表单提交
  // 如果注册成功，将显示已登录的用户名和“Logout”按钮
  const username = nameValue.split(' ')[0];
  document.getElementById('username').innerText = username;
  document.getElementById('username-label').style.display = 'inline-block';
  document.getElementById('login-button').style.display = 'none';
  document.getElementById('logout-button').style.display = 'inline-block';
  // 隐藏注册表单和其他按钮
  loginForm.style.display = 'block';
  registerForm.style.display = 'none';
  registerButton.style.display = 'none';
});