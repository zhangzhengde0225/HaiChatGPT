// 获取DOM元素
const loginForm = document.getElementById('login-form');
const registerButton = document.getElementById('register-button');
const sendCodeButton = document.getElementById('send-code-button');
const registerForm = document.getElementById('register-form');
const register_btn = document.getElementById('register-btn-in-form')


console.log('login.js loaded');
// console.log('register_btn: ', register_btn);


// 处理登录表单提交事件
loginForm.addEventListener('submit', (event) => {
  event.preventDefault(); // 阻止表单提交
  // console.log('submit event', event)
  const usernameValue = event.target.elements.username.value;
  const passwordValue = event.target.elements.password.value;
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
      localStorage.setItem('username', username);
      // 提示登录成功
      alert(`登录成功，欢迎您，${username}！`);
      window.location.href = '/';
    } else {
      // 登录失败，显示错误消息
      const message = data.message;
      alert(message);
    }
  })
  .catch(error => {
    console.error(error);
  });

});

// 显示注册表单
registerButton.addEventListener('click', () => {
  console.log('registerButton clicked');
  loginForm.style.display = 'none';
  // registerForm.style.display = 'block';
  const registerFormDIV = document.getElementById('register-form-div');
  registerFormDIV.style.display = 'block';
  // console.log('loginForm.style.display: ', loginForm.style.display);
  // console.log('registerForm.style.display: ', registerForm.style.display);
  // console.log(registerForm)
});


// 点击注册按钮
register_btn.addEventListener('click', (event) => {
  event.preventDefault(); // 阻止表单提交
  // console.log('register event', event)
  const nameValue = registerForm.elements.name.value
  const passwordValue = registerForm.elements.reg_password.value
  const phoneValue = registerForm.elements.phone.value
  const emailValue = registerForm.elements.reg_email.value
  if (!validatePasswordStrength(passwordValue)) {
    alert('密码必须大于等于6位且包含同时数字、字母和符号');
    return;
  }
  if (!validatePhoneNumber(phoneValue)) {
    alert('手机号码不正确');
    return;
  }
  if (!validateEmail(emailValue)) {
    alert('邮箱格式不正确');
    return;
  }
  
  // 在此处将用户名和密码发送给后台进行验证
  // 使用fetch API发送POST请求
  fetch('/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: nameValue,
      password: passwordValue,
      phone: phoneValue,
      email: emailValue,
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // 注册成功
      alert(`注册成功, ${nameValue}！`);
      window.location.href = 'login-dialog.html';
    } else {
      // 注册失败，显示错误消息
      const message = data.message;
      alert(`注册失败, ${message}！`);
    }
  })
  .catch(error => {
    console.error(error);
  });
});

// 验证手机号码
function validatePhoneNumber(phoneNumber) {
  var phonePattern = /^\d{11}$/;
  return phonePattern.test(phoneNumber);
}


// 验证密码强度，包含数字、字母、符号且长度大于等于6
function validatePasswordStrength(password) {
  var hasNumber = /\d/;
  var hasLetter = /[a-zA-Z]/;
  var hasSymbol = /[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]/;

  return (
    password.length >= 6 &&
    hasNumber.test(password) &&
    hasLetter.test(password) &&
    hasSymbol.test(password)
  );
}

// 验证邮箱格式
function validateEmail(email) {
  var emailPattern = /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/;
  return emailPattern.test(email);
}
