
// 主页上的用户名被点击事件

console.log("user_info.js loaded");
// console.log(window)

// user-info界面被加载时，从服务器获取用户信息
window.onload = function() {

    fetch("/get_user_data", {
        method: "GET",
        headers: {"Content-Type": "application/json"}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // update_user_info(data.user_data);
            console.log(data.user_data);
            update_user_info(data.user_data);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('user_info.js error', error);
    });
}

// 更新用户信息
function update_user_info(user_data) {
    const username_div = document.getElementById("username");
    const email_div = document.getElementById("email");
    const phone_div = document.getElementById("phone");
    const user_type_div = document.getElementById("user_type");
    const limit_div = document.getElementById("limit");
    const group_div = document.getElementById("group");
    const group_members_div = document.getElementById("group_members");
    const public_note_div = document.getElementById("public_note");

    // 如果用户为public或者Null, 则显示登录按钮
    local_user = localStorage.getItem("username");
    if (user_data.username == "public") {
        // public用户显示登陆按钮
        localStorage.setItem("username", null);
        public_note_div.parentNode.style.display = "flex";
        public_note_div.style.color = "red";
    }
    else if (user_data.username == null) {
        localStorage.setItem("username", null);
        alert("请先登录！");
        window.location.href = 'login-dialog.html';
        return;
    }

    // 更新信息
    username_div.innerText = user_data.username;
    if (user_data.email == "" || user_data.email == null) {
        user_data.email = "未填写";
        email_div.nextElementSibling.style.display = "flex";  // 显示填写按钮
    }
    email_div.innerText = user_data.email;

    if (user_data.phone == "" || user_data.phone == null) {
        user_data.phone = "未填写";
        phone_div.nextElementSibling.style.display = "flex";  // 显示填写按钮
        document.getElementById("send-code-button").innerHTML = "填写";
    }
    phone_div.innerText = user_data.phone;
    limit_div.innerText = '¥' + user_data.usage + '/¥' + user_data.limit;

    // free用户关闭群组的创建按钮
    if (user_data.user_type == "free") {
        group_div.nextElementSibling.style.display = "none";
    } 
    else if (user_data.user_type == "plus" || user_data.user_type == "admin") {
        group_div.nextElementSibling.style.display = "flex";    
    } 
    user_type_div.innerText = user_data.user_type;
    // 如果group为空，则显示无
    if (user_data.group == "" || user_data.group == null) {
        user_data.group = "无";
    }
    group_div.innerText = user_data.group;

    if (user_data.group_members == "" || user_data.group_members == null) {
        user_data.group_members = "无";
        group_members_div.style.display = "none";
    }
    else {
        group_members_div.parentNode.style.display = "flex";
        group_members_div.innerText = user_data.group_members;
    }
    
}

    