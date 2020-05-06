---
title: spring-cloud 分布式配置中心
date: 2019-11-12 22:40:35
tags: [config ,spring cloud ]
type: "categories"
categories: spring cloud
---

# 分布式配置中心（Dalston版本）

## 传统作法

​	通常在生产环境，Config Server与服务注册中心一样，我们也需要将其扩展为高可用的集群。在之前实现的config-server基础上来实现高可用非常简单，不需要我们为这些服务端做任何额外的配置，只需要遵守一个配置规则：将所有的Config Server都指向同一个Git仓库，这样所有的配置内容就通过统一的共享文件系统来维护，而客户端在指定Config Server位置时，只要配置Config Server外的均衡负载即可，就像如下图所示的结构：

![](config.png)

## 服务端 config-server

首先需要准备一个[git仓库](https://github.com/pignum1/config.git)，作为分布式配置的管理

创建idea的配置服务端,引入服务端的配置依赖

```groovy
implementation 'org.springframework.cloud:spring-cloud-config-server'
#刷新配置
implementation 'org.springframework.boot:spring-boot-starter-actuator'
```

在application.properties种添加配置文件和Git的地址，

```
#服务端口
server.port=9876
#服务名称
spring.application.name=myConfigServer
#服务注册中心

eureka.client.service-url.defaultZone=http://localhost:5678/eureka/
#服务的git仓库地址
spring.cloud.config.server.git.uri=https://github.com/pignum1/config.git
#配置文件所在的目录
spring.cloud.config.server.git.search-paths=/order
#配置文件所在的分支
spring.cloud.config.label=master

#spring cloud2.x刷新配置需要开启
management.endpoints.web.exposure.include=refresh,health,info
```

在启动类商添加注解

```
@EnableConfigServer
@SpringBootApplication
@ResponseBody
public class ConfigServerApplication {
	public static void main(String[] args) {
		SpringApplication.run(ConfigServerApplication.class, args);
	}
}
```

 启动服务后，按照配置文件的访问路径规则去请求

```
/{application}/{profile}[/{label}]
/{application}-{profile}.yml
/{label}/{application}-{profile}.yml
/{application}-{profile}.properties
/{label}/{application}-{profile}.properties
```

​		启动服务后访问 http://localhost:9876/order/a/master ，访问order文件下的order-a.properties文件，可以得到返回的数据

```
{
  "name": "order",
  "profiles": [
    "a"
  ],
  "label": "master",
  "version": "ab1b5e0ba15605570591d632977d8debcf7f77a9",
  "state": null,
  "propertySources": [
    {
      "name": "https://github.com/pignum1/config.git/order/order-a.properties",
      "source": {
        "from": "123"
      }
    }
  ]
}
```

这里的道德JSON字符串是因为我移除了spring cloud 默认的xml格式转换消息器 ,

在配置类中移除依赖

```
/**
 * 删除xml格式转换消息器
 */
configurations {
	all*.exclude group: 'com.fasterxml.jackson.dataformat', module: 'jackson-dataformat-xml'
}
```

## 客户端 config-client

同样创建一个spring cloud 项目，在依赖管理添加客户端的依赖

```
//客户端依赖
implementation 'org.springframework.cloud:spring-cloud-starter-config'
//mvc
implementation 'org.springframework.boot:spring-boot-starter-web'
#刷新配置
implementation 'org.springframework.boot:spring-boot-starter-actuator'
#注册中心依赖
implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
```

在resources下新建 bootstrap . yml文件，因为spring cloud的配置先读取的是bootstrap 文件。读取的顺序是bootstrap >连接config获取的配置文件> application 文件。否则启动时服务端拉数据的默认端口是8888

bootstrap . yml配置

```
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:5678/eureka/
spring:
  application:
    name: order
  cloud:
    config:
      uri: http://localhost:9876
      profile: a
      label: master

server:
  port: 8030

management:
  endpoints:
    web:
      exposure:
        include: refresh
```

此时启动客户端，控制台会打印下面的信息

![](console.png)

创建测试controller，这个

```
@RefreshScope
@RestController
public class TestController {

    @Value("${from}")
    private String from;

    @RequestMapping("/service")
    public String from() {

        return this.from;
    }

    public void setFrom(String from) {
        this.from = from;
    }

    public String getFrom() {
        return from;
    }
}
```

请求 http://localhost:8030/service ，页面上显示值为 123

如果这个时候修改order-a.properties 文件里面的from值为321，再次发起请求时页面仍未123，这时只要使用post方法请求  http://localhost:8030/actuator/refresh  刷新配置，再次请求http://localhost:8030/service ，页面上显示的值就成了321 。

## 添加重试机制

当该方法有很多服务，需要一个一个去刷新，一般使用 MQ+spring-could-bus 消息总线模式来批量更新配置信息。  还有一个附加的，就是在服务端在从配置中心获取配置信息时，如果出现了网络波动，导致项目启动时无法获取信息的话，可以使用如下配置来规避。
还是在config-client项目上进行扩展 依赖

```
#重试机制的依赖
implementation 'org.springframework.retry:spring-retry'
implementation 'org.springframework.boot:spring-boot-starter-aop'
```

在config的客户端  application.properties 添加配置

```
#retry
#和重试机制相关的配置有如下四个：
# 配置重试次数，默认为6
spring.cloud.config.retry.max-attempts=6
# 间隔乘数，默认1.1
spring.cloud.config.retry.multiplier=1.1
# 初始重试间隔时间，默认1000ms
spring.cloud.config.retry.initial-interval=1000
# 最大间隔时间，默认2000ms
spring.cloud.config.retry.max-interval=2000
```

在bootstrap .yml添加配置

```
#启动失败时能够快速响应
#spring:
		cloud:
			config:
				fail-fast=true
```







