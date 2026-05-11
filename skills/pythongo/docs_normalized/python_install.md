# 安装运行环境

> [!INFO]
> 使用 PythonGO，需要有编程经验，还需要有一定的英语水平，知道如何编辑 `.py` 文件，能自己解决 Python 安装过程遇到的问题，以及看懂 Python 的报错并解决。

### 下载安装包 [#download]

[下载卡片内容：原始组件 DownloadCard，建议补充为真实下载链接或在构建阶段注入链接数据]

### 解压安装包 [#decompress]

将压缩包解压后得到以下五个文件

```text
python3.12/
  python-3.12.*.exe
  requirements.txt
  unattend.xml
  安装依赖.exe
  安装依赖-备用.bat
```

### 安装 Python [#install]

运行 `python-3.12.*.exe`

点击 `Install`

![Python Install Step Image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240112095122.png)

安装完成后如果出现：`Disable path length limit`，请点击该项。

### 安装依赖 [#requirements]

双击运行文件夹中的 `安装依赖.exe` 文件，会开始下载并自动安装依赖库

> [!INFO]
> 如果 360 有报错或提示，请选择：允许该程序所有操作

> [!INFO]
> 如该程序运行失败（请先确保文件都解压出来了），则运行 `安装依赖-备用.bat`

### 开启 PythonGO 功能 [#enable-pythongo]

运行环境安装完成之后，还需要进行最后一步，去无限易客户端开启 PythonGO 功能，具体操作如下：

1. 打开无限易客户端并登录

2. 点击上方菜单栏「量化 - PythonGO」

3. 将「策略引擎」开关打开 （开关应为开启状态）

4. 点击切换版本按钮，切换为 ![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/switch_to_v2.svg)
