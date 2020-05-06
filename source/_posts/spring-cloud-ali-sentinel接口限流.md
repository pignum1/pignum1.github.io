---
title: spring-cloud-ali sentinel接口限流
date: 2019-12-08 20:43:17
tags: [sentinel,spring cloud alibaba ]
type: "categories"
categories: spring cloud alibaba 
---

# Sentinel是什么

​		Sentinel的官方标题是：分布式系统的流量防卫兵。从名字上来看，很容易就能猜到它是用来作服务稳定性保障的。对于服务稳定性保障组件，如果熟悉Spring Cloud的用户，第一反应应该就是Hystrix。但是比较可惜的是Netflix已经宣布对Hystrix停止更新。那么，在未来我们还有什么更好的选择呢？除了Spring Cloud官方推荐的resilience4j之外，目前Spring Cloud Alibaba下整合的Sentinel也是用户可以重点考察和选型的目标。 

# 使用Sentinel实现接口限流

 Sentinel的使用分为两部分： 

- sentinel-dashboard：与hystrix-dashboard类似，但是它更为强大一些。除了与hystrix-dashboard一样提供实时监控之外，还提供了流控规则、熔断规则的在线维护等功能。
- 客户端整合：每个微服务客户端都需要整合sentinel的客户端封装与配置，才能将监控信息上报给dashboard展示以及实时的更改限流或熔断规则等。

### 部署Sentinel Dashboard

[下载地址](https://github.com/alibaba/Sentinel/releases) 

下载到本地以后可以直接启动

```c
java -jar sentinel-dashboard-1.6.0.jar
```

sentinel-dashboard不像Nacos的服务端那样提供了外置的配置文件，比较容易修改参数。不过不要紧，由于sentinel-dashboard是一个标准的spring boot应用，所以如果要自定义端口号等内容的话，可以通过在启动命令中增加参数来调整，比如：`-Dserver.port=8888`。

默认情况下，sentinel-dashboard以8080端口启动，所以可以通过访问：`localhost:8080`来验证是否已经启动成功. 默认用户名和密码都是`sentinel` 

对于用户登录的相关配置可以在启动命令中增加下面的参数来进行配置：

- `-Dsentinel.dashboard.auth.username=sentinel`: 用于指定控制台的登录用户名为 sentinel；
- `-Dsentinel.dashboard.auth.password=123456`: 用于指定控制台的登录密码为 123456；如果省略这两个参数，默认用户和密码均为 sentinel
- `-Dserver.servlet.session.timeout=7200`: 用于指定 Spring Boot 服务端 session 的过期时间，如 7200 表示 7200 秒；60m 表示 60 分钟，默认为 30 分钟；

我是在阿里云上运行的，运行的命令是

```c
//后台启动的命令 
nohup java -jar sentinel-dashboard-1.6.0.jar >consoleMsg.log 2>&1 &
//查看jar进程的命令
ps aux|grep sentinel-dashboard-1.6.0.jar
//杀死进程
kill -9 30768
//查看日志
cat xxx.log  日志中有报错信息
//清空日志
echo " " >xxx.log
```

 nohup命令的作用就是让程序在后台运行，不用担心关闭连接进程断掉的问题了， 并且将标准输出的日志重定向至文件consoleMsg.log ,consoleMsg.log文件前提要创建好的,这个log文件最好跟jar包放一起 。 

# 整合Sentinel

创建一个新的springboot服务，命名为alibaba-sentinel-test1，添加依赖项

```groovy
	//sentinel
	compile group: 'com.alibaba.cloud', name: 'spring-cloud-starter-alibaba-sentinel', version: '2.1.0.RELEASE'
	//lombok
	compile group: 'org.projectlombok', name: 'lombok', version: '1.18.2'
```

修改配置文件

```properties
spring.application.name=alibaba-sentinel-test1
server.port=8002

# sentinel dashboard的访问地
spring.cloud.sentinel.transport.dashboard=localhost:8080
#延迟加载
#spring.cloud.sentinel.eager=true
```

添加请求方方法

```java
@RestController
public class TestController {

    @GetMapping(value = "/hello")
    public String hello() {
        return "Hello Sentinel";
    }
}
```

启动服务后，登录本地的sentinel页面（ http://localhost:8080/），并没有出现数据，这个时候发起请求

localhost:8002,页面上就显示如下图：

![](first-view.png)

点击 列表中的 簇点链路 ，点击/hello中的流控按钮，编辑限流单机阈值为2.

![](C:\Program Files\blog\source\_posts\spring-cloud-ali-sentinel接口限流\second-view.png)

点击新增之后，所有的规则都可以去流控规则列表中查看到.

## 验证限流规则

使用postman发起请求或者是curl发起请求测试

```
$ curl localhost:8002/hello
Hello Sentinel
$ curl localhost:8002/hello
Hello Sentinel
$ curl localhost:8002/hello
Blocked by Sentinel (flow limiting)
```

