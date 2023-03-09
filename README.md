# crawl
借助谷歌学术，从一些常用的出版社，根据期刊爬取论文信息。

## 安装方法
```bash
conda env create -n [name]
conda activate [name]
conda install python -c conda-forge
pip install bs4 selenium pandas
```

## 使用方法
```
1. 先利用 save_cookies.py 打开出版社网站，登录校园账号，保存 cookie 信息
2. 利用 crawl.py 爬取数据
3. 因为 google scholar 限制，仅允许访问最大 1000 条链接，所以如果某些期刊一年发文量大于 1000，仅返回1000条。
```

## 已知问题
```
1. Wiley 出版社用了访问安全机制，目前爬不了
2. 请先设置全局代理
```
