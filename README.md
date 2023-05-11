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
