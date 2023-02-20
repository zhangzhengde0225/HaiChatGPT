

## 科学上网客户端及配置方法

采用shadowsocks方案，支持win10, macos, linux, android, ios等系统。

### 1. 根据您的系统选择客户端安装：
+ Windows: [Shadowsocks-electron](https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/r05fCTTBEsSIpW1) v1.2.3
+ MacOS: [ShadowsocksX-NG](https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/Lq3erI8OTqiswky) v1.10
+ Linux: [Shadowsocks-electron](https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/GQKwS7iOl4Nr6xk) v1.2.3
+ Android: [Shadowsocks-android](https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/ctYj5QqIjdEJehp) v5.2.6
+ IOS: Potatso, apple应用商店搜索安装即可


如安装遇到问题，可以自行下载其他shadowsocks客户端。
例如shadowsocks-electron系列客户端v1.2.3[下载地址](https://github.com/nojsja/shadowsocks-electron/releases/tag/v1.2.3).

### 2. 卡密获取
+ 获取卡密请加小助手: 

    <img src="https://zhangzhengde0225.github.io/images/blog/ai4sci_ass.jpg" width=20%>

### 3. 配置方法

### Windows

windows客户端需启用http代理。

+ 1. 配置服务器卡密。设置地址、端口号、密码、加密方式等参数。
    <img src="https://zhangzhengde0225.github.io/images/blog/ss/edit_server.jpg" width="50%"/>
+ 2. 启用http代理。点击设置ss客户端`设置`，找到`http代理`，启用。如图打开了http代理，端口号`1095`；同时默认打开socks代理，端口号`1080`和pac代理，端口号`1090`。
    <img src="https://zhangzhengde0225.github.io/images/blog/ss/open_http_proxy.jpg" width="50%"/>
+ 3. Windows设置手动代理。点击桌面右下角`网络`→`网络和Internet设置`→`代理`→`手动设置代理`→`开`，设置代理地址为`127.0.0.1`(本机)、端口号为`1095`(ss客户端的http代理端口号)。
    <img src="https://zhangzhengde0225.github.io/images/blog/ss/windows_set_port.jpg" width="50%"/>
+ 4. 在ss客户端主页，右下角选择`全局`，右键服务器，点击`连接`，会显示`在线`。
    <img src="https://zhangzhengde0225.github.io/images/blog/ss/ss_online.jpg" width="50%"/>
+ 5. 验证，打开[谷歌学术](https://scholar.google.com/)，如果能打开，即说明能科学上网了。
+ 6. 使用结束后，请右键点击`断开连接`，取消手动代理设置。


### Linux

+ 1. 配置服务器和验证方法均与windows相同。
+ 2. Linux设置手动代理：打开`Settings`→`Network`，找到`Network Proxy`，点击配置，选择`Manual`，设置Socks Host为`127.0.0.1`，端口号为`1080`。
    <img src="https://zhangzhengde0225.github.io/images/blog/ss/linux_set_proxy.jpg" width="80%"/>


### MasOS

+ 使用ShadowsocksX-NG客户端，无需手动配置代理。

    <img src="https://zhangzhengde0225.github.io/images/blog/ss_macos_setting.jpg" width="50%"/>


如有问题可提Issue或联系：drivener@163.com。