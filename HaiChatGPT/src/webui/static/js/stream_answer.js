


console.log('stream_answer.js loaded');


function open_a_stream() {
// 该脚本用来监听和显示最后一次的回答，并流式显示
var source = new EventSource("/stream");
const md = window.markdownit();
// hljs.initHighlighting();  // 代码高亮的库
hljs.highlightAll();  // 代码高亮的库


source.onmessage = function(event) {
    if (event.data === "<|im_end|>") {
        source.close();
        document.getElementById("send-button").disabled = false;  // 启用send按钮
        return
    }
    document.getElementById("send-button").disabled = true;  // 禁用send按钮
    const markdownContent = document.getElementById('markdown_content');
    
    var html = event.data.replace(/<\|im_br\|>/g, '\n');
    html = md.render(html);
    // console.log(html);
    markdownContent.innerHTML = html;

    // 为每个代码块添加复制按钮
    document.querySelectorAll('pre code').forEach((codeBlock) => {
        const copyButton = document.createElement('button');  // 创建复制按钮
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';
        // 添加点击事件处理程序
        copyButton.addEventListener('click', () => {  // 复制代码块内容
        const codeText = codeBlock.innerText;
        const clipboard = new ClipboardJS(copyButton, {
            text: function() {
            return codeText;
            }
        });
        // 在按钮上显示复制成功提示
        clipboard.on('success', (e) => {
            e.trigger.textContent = 'Copied!';
            setTimeout(() => {
            e.trigger.textContent = 'Copy';
            }, 2000);
            e.clearSelection();
        });
        });

    // 添加代码块标题
    var class_name = codeBlock.className;  // 来自markdown自动渲染，格式为language-python
    var code_block_title = document.createElement("div");
    code_block_title.className = "code_block_title";
    if (class_name == "") {
    class_name = "code";
    }
    class_name = class_name.replace("language-", "");
    code_block_title.innerText = class_name;  
    code_block_title.appendChild(copyButton);
    copyButton.style.marginLeft = "auto";
    // 设置<pre>的样式
    codeBlock.parentNode.className = "code_block_pre";
    // // 设置自动调整尺寸，内部代码块自动换行
    // codeBlock.parentNode.style.overflow = "auto";
    
    // 设置codeBlock的字体
    codeBlock.style.fontFamily = "ColfaxAI";
    // codeBlock.style.backgroundColor = "#303030";
    // codeBlock.style.color = "#ffffff";
    
    // 将复制按钮插入到代码块前面
    codeBlock.parentNode.insertBefore(code_block_title, codeBlock);
    hljs.highlightBlock(codeBlock);
    });

    // 小代码块设置类名，便于css设置样式
    document.querySelectorAll('code').forEach((codeBlock) => {
        codeBlock.className = "small_code_block";
    });

    document.getElementById("output").scrollTop = document.getElementById("output").scrollHeight;
};
};

// 该脚本用来监听请求ip，显示在页面上，ip用于标识用户
var ip_source = new EventSource("/ip_addr");
ip_source.onmessage = function(event) {
  document.getElementById("ip_addr").innerHTML = "Your ip: " + event.data;
  ip_source.close();
};