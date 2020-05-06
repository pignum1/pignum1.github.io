---
title: mysql解决乱码
date: 2019-08-05 23:45:53
tags: [MySQL]
type: "categories"
categories: mysql
---
# 解决数据在MYSQL中文乱码的问题
@nbsp;@nbsp;@nbsp;@nbsp;最近自己在往阿里云服务器的数据库写数据的时候发现了中文乱码的问题
第一反应就编码格式不对，改成了utf还是乱码~~~唉,其实解决并不复杂

```
//首先编辑mysql的文件
vi /etc/my.cnf
//在[mysql]下添加
character-set-server=utf8
collation-server=utf8_general_ci
//在[client]下添加
default-character-set=utf8
//然后 esc  
//:wq  退出并保存
退出以后重启mysql
service mysqld restart
```
