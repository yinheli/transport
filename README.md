# transport

给亲爱的帅帅写的批处理工具

说实在的，我也不知道具体是做什么业务…… 😂

## 开发初始化

clone 项目后，做如下操作，初始化工程。

```bash
# 初始化虚拟环境
python3 -m venv --copies --clear .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# all done，可以愉快的开发和调试了 🎉
# 推荐开发工具： vscode、pycharm
```

## 打包

两种打包方式: `pyinstaller` & `shiv`，已经写好了脚本，任君选择。

## 常见问题

### 编码不支持？

运行时提示诸如

```
.....
.....
RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. Consult https://click.palletsprojects.com/python3/ for mitigation steps.

This system lists a couple of UTF-8 supporting locales that you can pick from.
.....
.....
```

```
# 看下系统里有哪些字符集
locale -a

# 选择支持中文 UTF-8 的

# 例如：
export LC_ALL=en_HK.utf8
export LANG=en_HK.utf8

# 或者：
export LC_ALL=zh_CN.utf8
export LANG=zh_CN.utf8
```

### 提示 GLIBC 不兼容？

运行预编译的二进制包报错，GLIBC 版本出现兼容问题。建议的解决方案有 2。

1. 找个老版本的 linux 系统（GLIBC）和目标系统兼容的版本，安装 python3，重新打包编译。
2. 在目标系统上安装 python3，然后执行 pyz 后缀结尾的 zip 运行包
