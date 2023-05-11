#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: chaichunyang@outlook.com

import json
import os
import sys
import time
from urllib.request import urlopen
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import logging

class Item:
    def __init__(self, extinf, url):
        self.extinf = extinf
        self.url = url
        self.speed = -1

    def __json__(self):
        return {'extinf': self.extinf, 'url': self.url, 'speed': self.speed}


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json__"):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


class Downloader:
    def __init__(self, url):
        self.url = url
        self.startTime = time.time()
        self.recive = 0
        self.endTime = None

    def getSpeed(self):
        if self.endTime and self.recive != -1:
            return self.recive / (self.endTime - self.startTime)
        else:
            return -1


def getAllM3UItems(dir):
    print('获取 %s 目录下的".m3u"文件...' % dir)
    files = []
    filenames = os.listdir(dir)
    pathnames = [os.path.join(dir, filename) for filename in filenames]
    for file in pathnames:
        if file.endswith('.m3u') and os.path.isfile(file):
            files.append(file)
    # 解析m3u文件
    items = []
    for file in files:
        with open(file, 'r+', encoding='utf-8') as f:
            extinf = ''
            for line in f:
                if line.startswith('#EXTM3U'):
                    continue
                if extinf:
                    items.append(Item(extinf.strip(), line.strip()))
                    extinf = ''
                if line.startswith('#EXTINF'):
                    extinf = line
    return items


def getStreamUrl(m3u8):
    urls = []
    try:
        prefix = m3u8[0:m3u8.rindex('/') + 1]
        with urlopen(m3u8, timeout=2) as resp:
            top = False
            second = False
            firstLine = False
            for line in resp:
                line = line.decode('utf-8')
                line = line.strip()
                # 不是M3U文件，默认当做资源流
                if firstLine and not '#EXTM3U' == line:
                    urls.append(m3u8)
                    firstLine = False
                    break
                if top:
                    # 递归
                    if not line.lower().startswith('http'):
                        line = prefix + line
                    urls += getStreamUrl(line)
                    top = False
                if second:
                    # 资源流
                    if not line.lower().startswith('http'):
                        line = prefix + line
                    urls.append(line)
                    second = False
                if line.startswith('#EXT-X-STREAM-INF:'):
                    top = True
                if line.startswith('#EXTINF:'):
                    second = True
            resp.close()
    except BaseException as e:
        print('get stream url failed! %s' % e)
    return urls


def downloadTester(downloader: Downloader):
    chunck_size = 10240
    try:
        resp = urlopen(downloader.url, timeout=2)
        # max 5s
        while(time.time() - downloader.startTime < 5):
            chunk = resp.read(chunck_size)
            if not chunk:
                break
            downloader.recive = downloader.recive + len(chunk)
        resp.close()
    except BaseException as e:
        print("downloadTester got an error %s" % e)
        downloader.recive = -1
    downloader.endTime = time.time()
def checkBandwidthThreshold(threshold=80*1024*1024):
    """
    检测本地网卡速度是否超过阈值
    :param threshold: 阈值，默认为1MB/s
    :return: bool
    """
    interface = 'WLAN'  # 网卡名称
    before = psutil.net_io_counters(pernic=True)[interface]
    time.sleep(1)
    after = psutil.net_io_counters(pernic=True)[interface]
    bytes_sent = after.bytes_sent - before.bytes_sent
    speed = bytes_sent / 1024 / 1024
    if speed > threshold: 
        return True 
    else: 
        return False




 # 定义任务处理函数
def process_item(item):
    while True:
        if checkBandwidthThreshold():
            print("超速")
            time.sleep(6)
        else:
            break
    idx = item.extinf.rindex(',') + 1
    print('测试：%s' % item.extinf[idx:])
    url = item.url
    stream_urls = []
    if url.lower().endswith('.flv'):
        stream_urls.append(url)
    else:
        stream_urls = getStreamUrl(url)
    # 速度默认-1
    speed = -1
    if len(stream_urls) > 0:
        print('流：%s'.format(str(stream_urls)))
        stream = stream_urls[0]
        downloader = Downloader(stream)
        downloadTester(downloader)
        speed = downloader.getSpeed()
    item.speed = speed
    print('\t速度：%d bytes/s' % item.speed)
    return item
 # 提交任务到线程池
def outputResults(items, filename, speed_threshold,first=0):
     # 检查result文件夹是否存在，如果不存在则创建它
    filename = 'result/'+filename
    if not os.path.exists('result'):
        os.makedirs('result')
    if  not os.path.isfile(filename) or first:
        with open(filename, "w") as file:
            print('#EXTM3U', file=file)
    if not len(items):
        return
    with open(filename, 'a+', encoding='utf-8') as f:
        for item in items:
            # 速度大于阈值
            if item.speed > speed_threshold:
                print(item.extinf, file=f)
                print(item.url, file=f)

def recorde(items,first=0):
     # while ing:
        # time.sleep(30)
        if first:
            print("正在初始化文件...")
        else:
            print('正在输出结果...')
        outputResults(items, 'useful.m3u', 1024 * 200,first)
        outputResults(items, 'good.m3u', 1024 * 500,first)
        outputResults(items, 'wonderful.m3u', 1024 * 700,first)
        outputResults(items, 'excellent.m3u', 1024 * 1024,first)
        time.sleep(2)
        
def start():
    path = os.getcwd()
    items = getAllM3UItems(path)
    dlan =len(items)
    
    if not dlan:
        print('没有找到任何源，退出。')
        sys.exit(0)
    print('发现项: %d' % dlan)
     # 创建线程池，指定最大线程数
    pool = ThreadPoolExecutor(max_workers=15)
     # 循环测速
    futures = [pool.submit(process_item, item) for item in items]
    ing =1
    # t1 = threading.Thread(target=recorde(items,ing))
    # t1.start()
      # 等待所有任务完成
    dates = []
    recorde(items,first=1)
    i=1
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    for future in as_completed(futures):
        if future.done():
            i=i+1
            result = future.result()
            dates.append(result)
            
            if i%50==0:
                ing = 1
                recorde(dates)
                logging.info("Progress: {:3}%".format(i*100/dlan))
                dates = []
                ing = 0
                
            # 处理任务结果
    ing = 0
    recorde(dates)
    # t1.join()
    outputResults(items, 'result.txt', 1024 * 200)
    print("完成并已记录")


if __name__ == '__main__':
    start()