# 金融行情爬虫 (ragent/test)

finance_crawler.py 是一个仅依赖 Python 标准库的爬虫小程序,
用于抓取腾讯财经 (qt.gtimg.cn) 的股票 / 指数实时行情。

## 运行

    python finance_crawler.py

## 输出

运行后会在本目录的 data/ 目录下生成带时间戳的文件:
- quote_YYYYMMDD_HHMMSS.csv  可用 Excel / pandas 打开
- quote_YYYYMMDD_HHMMSS.json 便于程序读取

## 说明

- 抓取的代码列表在脚本顶部的 CODES 变量中, 可自行增删 (指数示例 sh000001, 个股示例 sh600000 / sz000001)。
- 行情字段: 最新价、涨跌额、涨跌幅、今开、昨收、最高、最低、成交量、成交额、换手率、市盈率、市净率、振幅、量比、时间。
