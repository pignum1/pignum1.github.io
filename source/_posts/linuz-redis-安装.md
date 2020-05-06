---
title: linux redis 安装
date: 2019-08-08 01:15:44
tags: [redis,linux]
type: "categories"
categories: linx
---
```
#下载文件或者传到centos
wget http://download.redis.io/releases/redis-5.0.3.tar.gz
#解压文件
tar -zxvf redis-5.0.3.tar.gz
#cd切换到redis解压目录下，执行编译
cd redis-5.0.3
#编译
make
#安装并指定安装目录
make install PREFIX=/usr/local/redis
#修改 redis.conf 文件
 vi redis.confno
 //修改内容为daemonize no 改为 daemonize yes
 //		   bind 127.0.0.0 改为bind 0.0.0.0
 //        protected mode yes 改为 no
#指定配置文件启动 
./redis-server redis.conf
#添加开机启动服务
vi /etc/systemd/system/redis.service
//内容为
	[Unit]
	Description=redis-server
	After=network.target
	[Service]
	Type=forking
	ExecStart=/usr/local/redis/bin/redis-server /usr/local/redis/bin/redis.conf
	PrivateTmp=true
	[Install]
	WantedBy=multi-user.target
#设置开机启动
systemctl daemon-reload
systemctl start redis.service
systemctl enable redis.service
#创建 redis 命令软链接
ln -s /usr/local/redis/bin/redis-cli /usr/bin/redis

#服务操作命令
systemctl start redis.service   #启动redis服务
systemctl stop redis.service   #停止redis服务
systemctl restart redis.service   #重新启动服务
systemctl status redis.service   #查看服务当前状态
systemctl enable redis.service   #设置开机自启动
systemctl disable redis.service   #停止开机自启动
#其他常用命令
pkill redis  //停止redis
卸载redis：
rm -rf /usr/local/redis //删除安装目录
rm -rf /usr/bin/redis-* //删除所有redis相关命令脚本
```



