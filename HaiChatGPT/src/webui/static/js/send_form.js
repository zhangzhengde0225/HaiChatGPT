// 关于主页下方sendform的js

// 获取DOM元素

const sendForm = document.getElementById('send-form');
const prompt_text = document.getElementById('prompt');
const clearButton = document.getElementById('clear-button');
const last_question_div = document.getElementById('last_question');
const last_question_content = document.getElementById('last_question_content');
const last_answer_div = document.getElementById('last_answer');
const last_answer_content = document.getElementById('markdown_content');

console.log('send_form.js loaded');
prompt_text.focus();

// 事件监听
prompt_text.addEventListener('keydown', function(event) {
    // 按下shift+enter键，输入换行
    if (event.key === 'Enter' && event.shiftKey) {
        event.preventDefault();
        this.value += '\n';
    };
    // 按下ctrl+enter键，输入换行
    if (event.key === 'Enter' && event.ctrlKey) {
        event.preventDefault();
        this.value += '\n';
    };
    // 按下enter键，发送消息
    if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey) {
        event.preventDefault();
        document.getElementById('send-button').click();
    };
});


// 按enter发送消息，按shift+enter换行
sendForm.addEventListener('submit', (event) => {
    event.preventDefault(); // 阻止表单提交
    // 如果点击send按钮，就执行下面的函数
    if (event.submitter.id === 'send-button') {
        console.log('send pressed');
        submit_promt_form(event);  // 提交prmpt
    };
    // 如果点击enter键，就执行下面的函数
    if (event.key === 'Enter') {
        console.log('enter pressed');
        submit_promt_form(event);  // 也是提交prompt
    };
    // 点击clear按钮，就执行下面的函数
    if (event.submitter.id === 'clear-button') {
        console.log('clear pressed');
        // 清空输入框、
        submit_clear(event);
    };
});


function submit_promt_form(event) {
    const messageValue = event.target.elements.prompt.value;
    // 在此处将消息发送给后台
    // 使用fetch API发送POST请求

    // 禁用发送按钮
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = true;
    // 清空输入框
    event.target.elements.prompt.value = '';
    

    fetch('/send_prompt', {
        method: 'POST',
        headers: {  
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        message: messageValue
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
        // 发送成功
        // 清空输入框
        last_question_div.style.display = "flex";
        last_question_content.innerHTML = data.message;
        last_answer_div.style.display = "flex";
        last_answer_content.innerHTML = "正在等待...";

        open_the_history();
        open_a_stream();
        sendButton.disabled = false;  // 启用发送按钮
        } else {
        // 发送失败，显示错误消息
        const message = data.message;
        alert(message);
        }
    })
    .catch(error => {
        console.error(error);
    });
    };

// 点击清除按钮
// clearButton.addEventListener('click', (event) => {

function submit_clear(event) {
    // 发送清除请求，GET
    fetch('/clear', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        message: 'clear'
        })
    })  
    .then(response => response.json())
    .then(data => {
        if (data.success) {
        // 清除成功
        console.log('clear success');
        // 清空history
        document.getElementById('qa_pairs').innerHTML = '';
        } else {
        // 清除失败，显示错误消息
        const message = data.message;
        alert(message);
        }
    }
    )
    .catch(error => {
        console.error(error);
    }
    );
    
};

