# m3u-test
一个简单的检测m3u速度的py代码
用多线程进行了改进，并在运行过程中输出结果
增加了网卡速度检测，超过一定值线程暂停
网卡名称需要修改
以下是获得网卡名称方法

import netifaces
 # 获取系统中所有网卡信息
interfaces = netifaces.interfaces()
 # 遍历所有网卡并输出网卡名称
 
for interface in interfaces:

    print(interface)
    
  感谢 m3u-tester(https://github.com/chaichunyang/m3u-tester)) 为本项目提供了基础功能。
  
  脚本会检查当前目录下的.m3u文件，并测试所有检测到的视频流资源的网络连接速度

python3 m3u-tester.py

每个连接测试大约需要5秒左右的时间，如果资源较多，可能需要花费较长时间才能完成

测试完成后，会在当前目录生成result目录，写入以下文件：

result.json，所有测试的结果，包括extinf，url，speed

useful.m3u，速度大于200KB/sec

good.m3u，速度大于500KB/sec

wonderful.m3u，速度大于700KB/sec

excellent.m3u，速度大于1MB/sec
