# -*- coding: utf-8 -*-
# 腾讯财经行情爬虫: 抓取股票/指数实时行情, 结果保存到 data 目录
# 仅使用 Python 标准库, 无需安装第三方依赖
import csv
import datetime
import json
import os
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

API = 'https://qt.gtimg.cn/q='
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
BATCH_SIZE = 50

# 待抓取的股票 / 指数代码 (可自行增删)
CODES = [
    'sh000001', 'sz399001', 'sz399006', 'sh000300', 'sh000905', 'sh000016',
    'sh600000', 'sh600036', 'sh600519', 'sh601318', 'sh601398', 'sh601857',
    'sh601988', 'sh600030', 'sh600887', 'sh601888', 'sh600276', 'sh601012',
    'sh600585', 'sh601166', 'sh600900', 'sh601899', 'sh600028', 'sh601668',
    'sh600104', 'sh601628', 'sh601288', 'sh601939', 'sh601088', 'sh600809',
    'sh603288', 'sh688981', 'sh688111', 'sh688036', 'sh688012',
    'sz000001', 'sz000002', 'sz000333', 'sz000651', 'sz000858', 'sz002594',
    'sz300750', 'sz300059', 'sz002415', 'sz000725', 'sz002304', 'sz300015',
    'sz002714', 'sz000568', 'sz002352', 'sz300760', 'sz002027', 'sz000063',
    'sz002475', 'sz300124',
]

COLUMNS = ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '今开', '昨收', '最高',
           '最低', '成交量', '成交额', '换手率', '市盈率', '市净率', '振幅', '量比', '时间']

QUOTE = chr(34)


def batched(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def fetch(codes, retries=3):
    url = API + ','.join(codes)
    request = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.read().decode('gbk', errors='replace')
        except Exception as exc:
            print(f'  第 {attempt} 次请求失败: {exc}')
            time.sleep(2 * attempt)
    return ''


def to_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def parse(text):
    records = []
    for line in text.splitlines():
        if '=' not in line:
            continue
        payload = line.split('=', 1)[1].strip().rstrip(';').replace(QUOTE, '')
        parts = payload.split('~')
        if len(parts) < 50 or not parts[2]:
            continue
        records.append({
            '代码': parts[2],
            '名称': parts[1],
            '最新价': to_number(parts[3]),
            '涨跌额': to_number(parts[31]),
            '涨跌幅': to_number(parts[32]),
            '今开': to_number(parts[5]),
            '昨收': to_number(parts[4]),
            '最高': to_number(parts[33]),
            '最低': to_number(parts[34]),
            '成交量': to_number(parts[6]),
            '成交额': to_number(parts[37]),
            '换手率': to_number(parts[38]),
            '市盈率': to_number(parts[39]),
            '市净率': to_number(parts[46]),
            '振幅': to_number(parts[43]),
            '量比': to_number(parts[49]),
            '时间': parts[30],
        })
    return records


def save_csv(records, path):
    with open(path, 'w', newline='', encoding='utf-8-sig') as fp:
        writer = csv.DictWriter(fp, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def save_json(records, path):
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(records, fp, ensure_ascii=False, indent=2)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print('开始抓取腾讯财经实时行情 ...')
    records = []
    for group in batched(CODES, BATCH_SIZE):
        rows = parse(fetch(group))
        print(f'  本批请求 {len(group)} 个代码, 解析 {len(rows)} 条')
        records.extend(rows)
        time.sleep(1)
    print(f'共获取 {len(records)} 条行情记录')
    now = datetime.datetime.now()
    stamp = f'{now.year}{now.month:02d}{now.day:02d}_{now.hour:02d}{now.minute:02d}{now.second:02d}'
    csv_path = os.path.join(DATA_DIR, f'quote_{stamp}.csv')
    json_path = os.path.join(DATA_DIR, f'quote_{stamp}.json')
    save_csv(records, csv_path)
    save_json(records, json_path)
    print('CSV  ->', csv_path)
    print('JSON ->', json_path)


if __name__ == '__main__':
    main()
