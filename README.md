使用说明

## 1 环境安装

在控制台中依次执行以下脚本

```
# 创建虚拟环境
python3 -m venv venv

# 加载虚拟环境
.\venv\Scripts\activate

# 安装第三方模块（一行一行执行）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple beautifulsoup4
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple thefuzz
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple python-Levenshtein
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple openpyxl
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ddddocr
```

## 2. 自动答题

命令格式

```bash
python auto.py <username> <password> <school>
```

示例

```bash
python auto.py zhangsan 11111 辛安带专
```
