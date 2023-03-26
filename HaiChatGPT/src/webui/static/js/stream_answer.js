


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
    markdownContent.innerHTML = html;
    
    // 高亮代码块
    higtlight_code_block(markdownContent)

    document.getElementById("output").scrollTop = document.getElementById("output").scrollHeight;
    };
};

// 该脚本用来监听请求ip，显示在页面上，ip用于标识用户
var ip_source = new EventSource("/ip_addr");
ip_source.onmessage = function(event) {
  document.getElementById("ip_addr").innerHTML = "Your ip: " + event.data;
  ip_source.close();
};