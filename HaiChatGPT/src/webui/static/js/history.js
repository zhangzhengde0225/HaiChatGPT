



function open_the_history() {
    // 该脚本用来监听和显示历史聊天记录，即问答对
    // 监听请求qa_pairs，显示在页面上
    var qa_source = new EventSource("/qa_pairs");
    const md = window.markdownit();
    const qa_pairs_div = document.getElementById("qa_pairs");
    
    
    qa_source.onmessage = function(event) {
    if (event.data === "<|im_end|>") {
        qa_source.close();
        return
        };
    // 由于每次返回的所全部问答对，所以每次都要清空
    qa_pairs_div.innerHTML = "";  // 清空
    // 解析qa对，每对的分隔符是<|im_bbbr|>, qa的分隔符是<|im_sep|>
    var qa_pairs = event.data.split("<|im_bbbr|>");
    for (var i = 0; i < qa_pairs.length; i++) {
        var qa_pair = qa_pairs[i].split("<|im_sep|>");
        var qustion_div = document.createElement("div");  // 创建question_div
        var answer_div = document.createElement("div");  // 创建answer_div
        qustion_div.className = "question_div";
        answer_div.className = "answer_div";;
        // qustion_div.style.wordWrap = "break-word"; // 自动换行
        // answer_div.style.wordWrap = "break-word"; // 自动换行
        // qustion_div.style.whiteSpace = "pre-wrap"; // 自动换行, 会导致多行内容显示
        // answer_div.style.whiteSpace = "pre-wrap"; // 自动换行
        // question_div.style.wordWrap = "break-word"; // 自动换行
        // 添加图片
        var img = document.createElement("img");
        img.src = "/static/icons/user.png";
        img.className = "question_img";
        qustion_div.appendChild(img); 
        var ans_imge = document.createElement("img");
        ans_imge.src = "/static/icons/ai.png";
        ans_imge.className = "answer_img";
        answer_div.appendChild(ans_imge);
        
        // 添加问题和答案
        var q_html = qa_pair[0].replace(/<\|im_br\|>/g, '\n');
        // 两个\n\n会被转换成一个\n
        q_html = md.render(q_html);
        var a_html = qa_pair[1].replace(/<\|im_br\|>/g, '\n');
        a_html = md.render(a_html);
        
        var question_text = document.createElement("div");
        question_text.className = "markdown_content";
        question_text.innerHTML = q_html;
        var answer_text = document.createElement("div");
        answer_text.className = "markdown_content";
        answer_text.innerHTML = a_html;
        qustion_div.appendChild(question_text);
        answer_div.appendChild(answer_text);

        qa_pairs_div.appendChild(qustion_div);
        // 最后一个答案不添加
        // if (i != qa_pairs.length - 1) {
        //   document.getElementById("qa_pairs").appendChild(answer_div);
        // }
        qa_pairs_div.appendChild(answer_div);
        };
    
    // 高亮代码
    hljs.highlightAll();  // 代码高亮的库
    higtlight_code_block(qa_pairs_div);  // 为每个代码块添加复制按钮
    };
};


function higtlight_code_block(parent_div) {
    parent_div.querySelectorAll('pre code').forEach((codeBlock) => {
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
        
        // 将复制按钮插入到代码块前面
        codeBlock.parentNode.insertBefore(code_block_title, codeBlock);
        hljs.highlightElement(codeBlock);
        });
    parent_div.querySelectorAll('code').forEach((codeBlock) => {
        codeBlock.className = "small_code_block";
        });
}