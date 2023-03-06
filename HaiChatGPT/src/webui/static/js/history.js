// 该脚本用来监听和显示历史聊天记录，即问答对
// 监听请求qa_pairs，显示在页面上
var qa_source = new EventSource("/qa_pairs");
qa_source.onmessage = function(event) {
if (event.data === "<|im_end|>") {
    qa_source.close();
    return
    };
// 解析qa对，每对的换行符是<|im_br|>分隔符是<|im_sep|>
var qa_pairs = event.data.split("<|im_br|>");
for (var i = 0; i < qa_pairs.length; i++) {
    var qa_pair = qa_pairs[i].split("<|im_sep|>");
    var qustion_div = document.createElement("div");
    var answer_div = document.createElement("div");
    qustion_div.className = "question_div";
    answer_div.className = "answer_div";
    qustion_div.style.wordWrap = "break-word"; // 自动换行
    answer_div.style.wordWrap = "break-word"; // 自动换行
    // question_div.style.wordWrap = "break-word"; // 自动换行
    // 添加图片
    var img = document.createElement("img");
    img.src = "{{ url_for('static', filename='user.png') }}";
    img.className = "question_img";
    qustion_div.appendChild(img); 
    var ans_imge = document.createElement("img");
    ans_imge.src = "{{ url_for('static', filename='ai.png') }}";
    ans_imge.className = "answer_img";
    answer_div.appendChild(ans_imge);
    
    // 添加问题和答案
    // qustion_div.innerHTML = qa_pair[0];
    // answer_div.innerHTML = qa_pair[1];
    var question_text = document.createTextNode(qa_pair[0]);
    var answer_text = document.createTextNode(qa_pair[1]);
    qustion_div.appendChild(question_text);
    answer_div.appendChild(answer_text);

    document.getElementById("qa_pairs").appendChild(qustion_div);
    // 最后一个答案不添加
    // if (i != qa_pairs.length - 1) {
    //   document.getElementById("qa_pairs").appendChild(answer_div);
    // }
    document.getElementById("qa_pairs").appendChild(answer_div);
    
};
};