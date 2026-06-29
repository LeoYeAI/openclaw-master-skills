下载安装
--------

在安装Tushare前，需要提前安装好Python（建议是Python 3.7）环境，我们推荐[安装Anaconda](https://tushare.pro/document/1?doc_id=29)集成开发环境，并设置好环境变量。

-----



- 方式1：

	pip install tushare
	
  如果安装网络超时可尝试国内pip源，如pip install tushare -i https://pypi.tuna.tsinghua.edu.cn/simple <br>  <br>
- 方式2：访问<a href="https://pypi.python.org/pypi/tushare/" target="_blank">https://pypi.python.org/pypi/tushare/</a>下载安装 ，执行 python setup.py install<br> <br>
- 方式3：访问<a href="https://github.com/waditu/tushare" target="_blank">https://github.com/waditu/tushare</a>,将项目下载或者clone到本地，进入到项目的目录下，
  执行： python setup.py install

<br>
<br>

版本升级
--------

---------


	 pip install tushare --upgrade

<br>

查看当前版本的方法：

	import tushare
	
	print(tushare.__version__)