



function open_the_history() {
    // 该脚本用来监听和显示历史聊天记录，即问答对
    // 监听请求qa_pairs，显示在页面上
    var qa_source = new EventSource("/qa_pairs");
    const md = window.markdownit();
    hljs.highlightAll();  // 代码高亮的库
    
    
    qa_source.onmessage = function(event) {
    if (event.data === "<|im_end|>") {
        qa_source.close();
        return
        };
    // 由于每次返回的所全部问答对，所以每次都要清空
    document.getElementById("qa_pairs").innerHTML = "";  // 清空
    // 解析qa对，每对的分隔符是<|im_bbbr|>, qa的分隔符是<|im_sep|>
    var qa_pairs = event.data.split("<|im_bbbr|>");
    for (var i = 0; i < qa_pairs.length; i++) {
        var qa_pair = qa_pairs[i].split("<|im_sep|>");
        var qustion_div = document.createElement("div");  // 创建question_div
        var answer_div = document.createElement("div");  // 创建answer_div
        qustion_div.className = "question_div";
        answer_div.className = "answer_div";
        // qustion_div.style.wordWrap = "break-word"; // 自动换行
        // answer_div.style.wordWrap = "break-word"; // 自动换行
        qustion_div.style.whiteSpace = "pre-wrap"; // 自动换行
        answer_div.style.whiteSpace = "pre-wrap"; // 自动换行
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
        // qustion_div.innerHTML = qa_pair[0];
        // answer_div.innerHTML = qa_pair[1];
        var q_html = qa_pair[0].replace(/<\|im_br\|>/g, '\n');
        q_html = md.render(q_html);
        var a_html = qa_pair[1].replace(/<\|im_br\|>/g, '\n');
        a_html = md.render(a_html);
        // var question_text = document.createTextNode(q_html);
        // var answer_text = document.createTextNode(a_html);
        var question_text = document.createElement("div");
        question_text.innerHTML = q_html;
        var answer_text = document.createElement("div");
        answer_text.innerHTML = a_html;
        qustion_div.appendChild(question_text);
        answer_div.appendChild(answer_text);

        document.getElementById("qa_pairs").appendChild(qustion_div);
        // 最后一个答案不添加
        // if (i != qa_pairs.length - 1) {
        //   document.getElementById("qa_pairs").appendChild(answer_div);
        // }
        document.getElementById("qa_pairs").appendChild(answer_div);

        parent_selector = document.getElementById("qa_pairs");
        add_copy_button_to_pre_code(parent_selector);  // 为每个代码块添加复制按钮
        // set_all_code_classname(parent_selector);  // 为每个代码块添加复制按钮
        
    };
    };
};