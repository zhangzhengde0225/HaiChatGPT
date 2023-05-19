

const dropzone = document.getElementById('drop-zone');
const filepath = document.getElementById('file-path');
const file_remove_btn  = document.getElementById('file-remove');
file_remove_btn.style.display = 'none';

// 拖到到此处时，改变样式
dropzone.addEventListener('dragover', function(e) {
  e.preventDefault(); // 阻止浏览器默认行为
  // console.log('dragover');
  if (dropzone.style.background != '#aeb7dd') {
    dropzone.style.background = '#aeb7dd';
  }
});

// 离开此处时，改变样式
dropzone.addEventListener('dragleave', function(e) {
  e.preventDefault(); // 阻止浏览器默认行为
  // console.log('dragleave');
  if (dropzone.style.background != '#c7cce2') {
    dropzone.style.background = '#c7cce2';
  }
});

// 放下时，改变样式
dropzone.addEventListener('drop', function(e) {
  e.preventDefault(); // 阻止浏览器默认行为，否则会打开文件
  var files = e.dataTransfer.files; // 获取拖拽的文件列表
  // console.log(files);
  var file = files[0]; // 获取第一个文件
  // 处理文件列表
  dropzone.style.background = '#c7cce2';
  filepath.innerHTML = file.name + '  ';
  file_remove_btn.style.display = 'flex';
  dropzone.style.display = 'none';

  // var reader = new FileReader();
  // reader.onload = function() {
  //   filepath.innerText = this.result;  // 读取文件内容
  // };
  // reader.readAsText(file);

  // 上传文件
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload', true);
  xhr.onload = function() {
    if (xhr.status === 200) {
      // console.log(xhr.responseText);
      // 解析返回的json数据
      var data = JSON.parse(xhr.responseText);
      if (data.success) {
        // 上传成功
        var num_tokens = data.message;
        var msg = '上传成功！' +  num_tokens + '个Tokens';
        filepath.innerHTML += ' ' + num_tokens + 'Tokens';
        console.log(msg);
      } else {
        // 上传失败
        var msg = '上传失败！'+ data.message;
        filepath.innerHTML = '';
        file_remove_btn.style.display = 'none';
        dropzone.style.display = 'flex';
        alert(msg);
      }
    } else {
      alert('网络原因上传失败！');
      filepath.innerHTML = '';
      file_remove_btn.style.display = 'none';
      dropzone.style.display = 'flex';
    }
  };
  var formData = new FormData();
  formData.append('file', file);
  xhr.send(formData)

});


// 点击删除按钮时，清空文件路径
file_remove_btn.addEventListener('click', function(e) {
  e.preventDefault(); // 阻止浏览器默认行为
  filepath.innerHTML = '';
  file_remove_btn.style.display = 'none';
  dropzone.style.display = 'flex';
  // 发送请求，删除文件
  fetch('/delete_tmp_sys_prompt', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // 删除成功
      console.log('删除成功！');
    } else {
      // 删除失败
      console.log('删除失败！');
    }
  })
});
