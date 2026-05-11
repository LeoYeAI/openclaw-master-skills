# 常见问题

### 我需要具备什么能力才能使用 PythonGO

需要能看懂 Python 代码，有 Python 基础，有阅读英语报错的能力，一般来讲具备以上能力就可以解决大部分问题。当然最重要的还是仔细阅读文档

### 新版本的代码可以在 Python 3.8 环境中运行吗

不可以，当前代码已经全部采用最新的语法编写，只支持 Python 3.12

### 如何查看 `INFINIGO` 的源代码

`INFINIGO` 是一个 `CAPI` 库，其作用是让 PythonGO 能和无限易进行交互，里面的源代码只是一些获取数据的函数，而 PythonGO 重新封装了这些函数，所以你无需查看 `INFINIGO` 的源代码即可进行开发，文档以及代码中的注释会帮你理解这个库

### 推荐用什么编辑器来编写代码

[Visual Studio Code](https://code.visualstudio.com/)

### PythonGO 合成的 K 线指标和别的软件不一样

合成 K 线数据的标准不一样，计算指标标准也不一样，PythonGO 的计算指标结果和无限易是一致的

### 如何查看 PythonGO 的完整错误日志

点击 PythonGO 窗口的「控制台」右上角文件按钮 ![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/folder.svg)，就可以打开完整的日志文件，拉到最下面就是最新的日志

### Exception: REQUEST_EXPIRED 签名验证错误: 请求已过期

* 电脑时间和北京时间有差异，需要校准时间
  * 如果电脑时间是对的，则需要在网络设置中关闭 IPv6 功能

### PythonGo目录未找到

先把 Python 卸载，然后打开目录 `%localappdata%\Programs\Python`，找到 Python 开头的目录并删掉，再按照安装文档重新安装 Python

### 可不可以调用外部库

可以，这是 Python 代码，不要被框架受限

### 可不可以回测

可以，请查看回测部分教程

### 可不可以用编辑器运行代码

不可以

### 可不可以连接数据库

可以

### 我的策略会不会被泄露

不会，策略只会存在自己电脑上
