# 调试

过去我们使用 PythonGO 的时候，只能使用 `self.output` 输出变量值的方法来「调试」我们的策略，而且只能一行行输出，每次新增或删除 `self.output` 代码，都需要重载策略，这很不方便。

现在 PythonGO 支持**直接通过编辑器来调试策略文件**，可以断点，可以监视变量，可以让我们的编程效率进一步提高。

> [!INFO]
> 此教程仅适用于进阶用户

> [!INFO]
> 仅 `v2026.0105` 及之后的无限易版本支持调试

## 使用 VS Code 进行调试 [#debugging-with-vs-code]

主要流程大概是：策略启动调试服务，编辑器去连接调试服务，连接成功后，就可以直接在编辑器断点调试了。

我们先在想要调试的策略代码中添加启动调试服务的代码：

```py
from pythongo.debug_utils import start_remote_debug

start_remote_debug()
```

只需要在策略代码顶部写下这两行即可，之后当我们加载策略的时候，会打印日志：

```text
[Debug] 服务监听中 (端口 5678)...
[Debug] 等待 VS Code 连接...
```

此时调试服务就启动成功了，策略也会被阻塞，等待编辑器去连接调试服务。

> [!ERROR]
> 如果提示 `ModuleNotFoundError: No module named 'debugpy'`，需要打开 `CMD`，执行 `pip install debugpy` 来安装依赖。

这个时候我们回到编辑器，**需要确保我们处于工作目录中**（如果不知道什么是工作目录，请回看 [第一个策略 - 编写策略 - 工作目录](/tutorial/first_strategy#work-directory)），我们在工作目录的根目录，也就是和 `pythongo` 文件夹同级的目录，新建一个 `.vscode` **文件夹**，一般这个文件夹都存在，如果没有则手动创建。然后在 `.vscode` 文件夹里新建一个 `launch.json` 文件，并添加以下内容：

```json filename="launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: PythonGO 策略调试",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "127.0.0.1",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "${workspaceFolder}"
        }
      ],
      "justMyCode": false
    }
  ]
}
```

这是新建好文件后的目录结构：

```text
pyStrategy/
  .vscode/
    launch.json
  demo/
    instance_files/
      pythongo/
        self_strategy/
```

`launch.json` 文件创建好后，如果需要调试的策略已经加载了，提示等待连接，那就可以在编辑器中按下 `F5` 快捷键来启动调试。

如果 `F5` 快捷键被别的应用程序占用了，也可以在编辑器最左侧找到「运行和调试」按钮（一只虫子趴在右三角上），点击之后调试下拉框会出现我们刚给添加的选项，选中后点击绿色的启动调试按钮，即可开始调试：

![VS Code Debug Interface](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20260206154652.png)

此时 PythonGO 日志窗口应该提示连接成功：

```text {3}
[Debug] 服务监听中 (端口 5678)...
[Debug] 等待 VS Code 连接...
[Debug] 连接成功！
```

这个时候就可以在 PythonGO 框架下的**任意代码**中打断点调试，只要代码被执行到了，就会进入断点，接下来就可以自行调试策略了，效果如下：

![VS Code Debug Interface](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20260206160936.png)

## 使用 PyCharm 进行调试 [#debugging-with-pycharm]

PyCharm Community（免费社区版）不支持远程调试

PyCharm Professional（付费专业版）不支持 PythonGO 的调试方法
