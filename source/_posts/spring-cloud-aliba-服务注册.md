---
title: spring-cloud-aliba 服务注册
date: 2019-12-03 20:51:22
tags: [nacos,spring cloud alibaba ]
type: "categories"
categories: spring cloud alibaba 
---

# 服务注册

 Nacos致力于帮助您发现、配置和管理微服务。Nacos提供了一组简单易用的特性集，帮助您快速实现动态服务发现、服务配置、服务元数据及流量管理。Nacos帮助您更敏捷和容易地构建、交付和管理微服务平台。Nacos是构建以“服务”为中心的现代应用架构 (例如微服务范式、云原生范式) 的服务基础设施 

[nacos下载地址]( https://github.com/alibaba/nacos/releases )

我下载的版本是1.1.4

 下载完成之后，解压。根据不同平台，执行不同命令，启动单机版Nacos服务： 

- Linux/Unix/Mac：`sh startup.sh -m standalone`
- Windows：`cmd startup.cmd -m standalone`

 `startup.sh`脚本位于Nacos解压后的bin目录下。这里主要介绍Spring Cloud与Nacos的集成使用，对于Nacos的高级配置，后续再补充。 启动完成之后，访问：`http://127.0.0.1:8848/nacos/`，可以进入Nacos的服务管理页面， 出现登录页面，默认用户名密码为：nacos 

## 构建应用接入Nacos注册中心

 在完成了Nacos服务的安装和启动之后，下面我们就可以编写两个应用（服务提供者与服务消费者）来验证服务的注册与发现了。 

### 服务提供者

 **第一步**：创建一个Spring Boot应用，可以命名为：`alibaba-nacos-discovery-server` 

引入依赖,这两个依赖还没有在spring cloud 官方版本，所以需要手动引入

```
	// ali depence
	compile group: 'com.alibaba.cloud', name: 'spring-cloud-starter-alibaba-nacos-discovery', version: '2.1.0.RELEASE'

	// https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-alibaba-nacos-discovery
	compile group: 'org.springframework.cloud', name: 'spring-cloud-starter-alibaba-nacos-discovery', version: '0.9.0.RELEASE'
```

在启动类上添加注解

```java
@EnableDiscoveryClient
@SpringBootApplication
public class AlibabaNacosDiscoveryServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(AlibabaNacosDiscoveryServerApplication.class, args);
	}

}
```

创建一个服务提供方法类

```java
@RestController
public class TestController {

    @GetMapping("/hello")
    public String hello(@RequestParam String name) {
        return "hello " + name;
    }
}
```

在配置文件application.properties中配置服务名称和Nacos地址 

```properties
spring.application.name=alibaba-nacos-discovery-server
server.port=8001

spring.cloud.nacos.discovery.server-addr=localhost:8848
spring.main.allow-bean-definition-overriding=true
```

启动服务，这个时候可以在 http://127.0.0.1:8848/nacos/ 服务列表上看见

![](server.png)

### 服务消费者

创建一个Spring Boot应用，命名为：`alibaba-nacos-discovery-client-common`。引入依赖

```groovy
	implementation 'org.springframework.boot:spring-boot-starter-web'

	// ali depence
	compile group: 'com.alibaba.cloud', name: 'spring-cloud-starter-alibaba-nacos-discovery', version: '2.1.0.RELEASE'

	// https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-alibaba-nacos-discovery
	compile group: 'org.springframework.cloud', name: 'spring-cloud-starter-alibaba-nacos-discovery', version: '0.9.0.RELEASE'
```

在启动类上添加注解

```java
@EnableDiscoveryClient
@SpringBootApplication
@EnableFeignClients
public class AlibabaNacosDiscoveryClientCommonApplication {

	public static void main(String[] args) {
		SpringApplication.run(AlibabaNacosDiscoveryClientCommonApplication.class, args);
	}


	@RestController
	static class TestController {

		//负载均衡
		@Autowired
		LoadBalancerClient loadBalancerClient;

		@Bean
		@LoadBalanced
		public RestTemplate restTemplate() {
			return new RestTemplate();
		}

		@Bean
		@LoadBalanced
		public WebClient.Builder loadBalancedWebClientBuilder() {
			return WebClient.builder();
		}
	}
}
```

创建服务消费方法

```java
@RestController
public class TestController {

    @Autowired
    LoadBalancerClient loadBalancerClient;

    @Autowired
    RestTemplate restTemplate;

    @Autowired
    TestInterface testInterface;

    @Autowired
    private WebClient.Builder webClientBuilder;


    @GetMapping("/test")
    public String test() {
        // 通过spring cloud common中的负载均衡接口选取服务提供节点实现接口调用
        ServiceInstance serviceInstance = loadBalancerClient.choose("alibaba-nacos-discovery-server");
        String url = serviceInstance.getUri() + "/hello?name=" + "panghu";
        RestTemplate restTemplate = new RestTemplate();
        String result = restTemplate.getForObject(url, String.class);
        return "Invoke : " + url + ", return : " + result;
    }

    @GetMapping("/test2")
    public String test2() {
        String result = restTemplate.getForObject("http://alibaba-nacos-discovery-server/hello?name=panghu", String.class);
        return "Return : " + result;
    }

    @GetMapping("/test3")
    public Mono<String> test3() {
        Mono<String> result = webClientBuilder.build()
                .get()
                .uri("http://alibaba-nacos-discovery-server/hello?name=panghu")
                .retrieve()
                .bodyToMono(String.class);
        return result;
    }

    @GetMapping("/test4")
    public String test4() {
        String result = testInterface.hello("panghu");
        return "Return : " + result;
    }
}
```

创建fegin的调用接口

```java
@FeignClient("alibaba-nacos-discovery-server")
public interface TestInterface {

    @GetMapping("/hello")
    String hello(@RequestParam(name = "name") String name);
}
```

这个时候启动消费者、提供者，在本地输入 http://localhost:8003/test1, http://localhost:8003/test2 , http://localhost:8003/test3 , http://localhost:8003/test4 .使用不同的方法调用服务。

# 使用nacos构建配置中心

Nacos除了实现了服务的注册发现之外，还将配置中心功能整合在了一起。通过Nacos的配置管理功能，我们可以将整个架构体系内的所有配置都集中在Nacos中存储。这样做的好处，在以往的教程中介绍Spring Cloud Config时也有提到，主要有以下几点：

- 分离的多环境配置，可以更灵活的管理权限，安全性更高
- 应用程序的打包更为纯粹，以实现一次打包，多处运行的特点

## 创建配置

 第一步：进入Nacos的控制页面，在配置列表功能页面中，点击右上角的“+”按钮，进入“新建配置”页面，如下图填写内容： 

![](config.png)

其中：

- `Data ID`：填入`alibaba-nacos-config-client.properties`
- `Group`：不修改，使用默认值`DEFAULT_GROUP`
- `配置格式`：选择`Properties`
- `配置内容`：应用要加载的配置内容，这里仅作为示例，做简单配置，比如：`panghu.title.title=spring-cloud-alibaba-learning`

## 创建应用

引入依赖

```groovy
	// https://mvnrepository.com/artifact/com.alibaba.cloud/spring-cloud-starter-alibaba-nacos-config
	compile group: 'com.alibaba.cloud', name: 'spring-cloud-starter-alibaba-nacos-config', version: '2.1.0.RELEASE'

	// ali depence
	compile group: 'com.alibaba.cloud', name: 'spring-cloud-starter-alibaba-nacos-discovery', version: '2.1.0.RELEASE'

	// https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-alibaba-nacos-discovery
	compile group: 'org.springframework.cloud', name: 'spring-cloud-starter-alibaba-nacos-discovery', version: '0.9.0.RELEASE'
```

 在启动类应中实现一个HTTP接口验证配置文件加载是否成功

```java
@SpringBootApplication
public class AlibabaNacosConfigClientApplication {

	public static void main(String[] args) {
		SpringApplication.run(AlibabaNacosConfigClientApplication.class, args);
	}

	@RestController
	@RefreshScope
	static class TestController {
		@Value("${panghu.title:}")
		private String title;
		@GetMapping("/test")
		public String hello() {
			return title;
		}
	}
}
```

 		内容非常简单，`@SpringBootApplication`定义是个Spring Boot应用；还定义了一个Controller，其中通过`@Value`注解，注入了key为panghu.title`的配置（默认为空字符串），这个配置会通过`/test`接口返回，后续我们会通过这个接口来验证Nacos中配置的加载。另外，这里还有一个比较重要的注解`@RefreshScope`，主要用来让这个类下的配置内容支持动态刷新，也就是当我们的应用启动之后，修改了Nacos中的配置内容之后，这里也会马上生效。 

​		创建配置文件`bootstrap.properties`，并配置服务名称和Nacos地址 ，SpringCloudConfig和 NacosConfig这种统一配置服务在springboot项目中初始化时，都是加载bootstrap.properties配置文件去初始化上下文。这是由spring boot的加载属性文件的优先级决定的，想要在加载属性之前去config server上取配置文件，NacosConfig或SpringCloudConfig相关配置就是需要最先加载的，而bootstrap.properties的加载是先application.properties的，所以config client要配置config的相关配置就只能写到bootstrap.properties里了

```properties
spring.application.name=alibaba-nacos-config-client
server.port=8001
spring.cloud.nacos.discovery.server-addr=127.0.0.1:8848
spring.main.allow-bean-definition-overriding=true
spring.cloud.nacos.config.server-addr=127.0.0.1:8848
```

启动服务后访问 http://localhost:8001/test ，显示页面如下所示

![](config-server.png)

# Nacos配置的加载规则详解

，Nacos中创建的配置内容是这样的：

- `Data ID`：alibaba-nacos-config-client.properties
- `Group`：DEFAULT_GROUP

拆解一下，主要有三个元素，它们与具体应用的配置内容对应关系如下：

- Data ID中的`alibaba-nacos-config-client`：对应客户端的配置`spring.cloud.nacos.config.prefix`，默认值为`${spring.application.name}`，即：服务名
- Data ID中的`properties`：对应客户端的配置`spring.cloud.nacos.config.file-extension`，默认值为`properties`
- Group的值`DEFAULT_GROUP`：对应客户端的配置`spring.cloud.nacos.config.group`，默认值为`DEFAULT_GROUP`

在采用默认值的应用要加载的配置规则就是：`Data ID=${spring.application.name}.properties`，`Group=DEFAULT_GROUP`。

下面，我们做一些假设例子，方便大家理解这些配置之间的关系：

**例子一**：如果我们不想通过服务名来加载，那么可以增加如下配置，就会加载到`Data ID=example.properties`，`Group=DEFAULT_GROUP`的配置内容了：

```properties
spring.cloud.nacos.config.prefix=example
```

**例子二**：如果我们想要加载yaml格式的内容，而不是Properties格式的内容，那么可以通过如下配置，实现加载`Data ID=example.yaml`，`Group=DEFAULT_GROUP`的配置内容了：

```properties
spring.cloud.nacos.config.prefix=example
spring.cloud.nacos.config.file-extension=yaml
```

**例子三**：如果我们对配置做了分组管理，那么可以通过如下配置，实现加载`Data ID=example.yaml`，`Group=DEV_GROUP`的配置内容了：

```properties
spring.cloud.nacos.config.prefix=example
spring.cloud.nacos.config.file-extension=yaml
spring.cloud.nacos.config.group=DEV_GROUP
```

## 多环境管理

 在Nacos中，本身有多个不同管理级别的概念，包括：`Data ID`、`Group`、`Namespace`。只要利用好这些层级概念的关系，就可以根据自己的需要来实现多环境的管理。 

`Data ID`在Nacos中，我们可以理解为就是一个Spring Cloud应用的配置文件名,我们知道默认情况下`Data ID`的名称格式是这样的：`${spring.application.name}.properties`，即：以Spring Cloud应用命名的properties文件。

实际上，`Data ID`的规则中，还包含了环境逻辑，这一点与Spring Cloud Config的设计类似。我们在应用启动时，可以通过`spring.profiles.active`来指定具体的环境名称，此时客户端就会把要获取配置的`Data ID`组织为：`${spring.application.name}-${spring.profiles.active}.properties`。

 实际上，更原始且最通用的匹配规则，是这样的：`${spring.cloud.nacos.config.prefix}`-`${spring.profile.active}`.`${spring.cloud.nacos.config.file-extension}`。而上面的结果是因为`${spring.cloud.nacos.config.prefix}`和`${spring.cloud.nacos.config.file-extension}`都使用了默认值。 

### 使用后缀实现

测试在nacos中创建一个新的配置文件 alibaba-nacos-config-client-dev.properties

```properties
panghu.title=7654321
```

在配置文件中添加spring.profiles.active=dev，

```properties
spring.application.name=alibaba-nacos-config-client
server.port=8001

spring.cloud.nacos.discovery.server-addr=127.0.0.1:8848
spring.main.allow-bean-definition-overriding=true

#spring.cloud.nacos.config.prefix=example
spring.cloud.nacos.config.server-addr=127.0.0.1:8848
spring.profiles.active=dev
```

重新启动服务，访问 http://localhost:8001/test 可以发现打印出的结果是7654321

### 使用`Group`实现

测试在nacos中创建一个新的配置文件 alibaba-nacos-config-client.properties

![](config-group.png)

在配置文件中添加

```properties
spring.application.name=alibaba-nacos-config-client
server.port=8001

spring.cloud.nacos.discovery.server-addr=127.0.0.1:8848
spring.main.allow-bean-definition-overriding=true

#spring.cloud.nacos.config.prefix=example
spring.cloud.nacos.config.server-addr=127.0.0.1:8848
spring.profiles.active=dev
spring.cloud.nacos.config.group=DEV_GROUP
```

再次重新启动服务，访问 http://localhost:8001/test 可以发现打印出的结果是1234567

### 使用`Namespace`实现

 **第一步**：先在Nacos中，根据环境名称来创建多个`Namespace`。比如： 

![](namespace.png)

在dev分支下创建配置文件

![](namespace-dev.png)

在启动的配置文件中添加

```properties
spring.cloud.nacos.config.namespace=d8b4a958-e2e8-4ed7-be64-69646aeb42c0
```

 分别利用Nacos配置管理功能中的几个不同纬度来实现多环境的配置管理。

## 加载多个配置文件

在配置中心添加两个配置文件

a.properties

```properties
a.name=a
```

b.properties

```properties
b.name=b
```

在springBoot的配置文件中添加

```properties
spring.cloud.nacos.config.ext-config[0].dataId=a.properties
spring.cloud.nacos.config.ext-config[0].group=DEFAULT_GROUP
spring.cloud.nacos.config.ext-config[0].refresh=true
spring.cloud.nacos.config.ext-config[1].data-id=b.properties
spring.cloud.nacos.config.ext-config[1].group=DEFAULT_GROUP
spring.cloud.nacos.config.ext-config[1].refresh=true
```

修改测试方法

```java
	@RestController
	@RefreshScope
	static class TestController {

		@Value("${panghu.title:}")
		private String title;

		@Value( "${a.name:}" )
		private String aname;

		@Value( "${b.name:}" )
		private String bname;

		@GetMapping("/test")
		public String hello() {
			return title+"_____a:"+aname+"_____b:"+bname;
		}

	}
```

重启服务访问http://localhost:8001/test 可以发现打印出的结果是 spring-cloud-alibaba-learning_____a:a_____b:b 

## 共享配置

通过上面加载多个配置的实现，实际上我们已经可以实现不同应用共享配置了。但是Nacos中还提供了另外一个便捷的配置方式，比如下面的设置与上面使用的配置内容是等价的：

```properties
spring.cloud.nacos.config.shared-dataids=actuator.properties,log.properties
spring.cloud.nacos.config.refreshable-dataids=actuator.properties,log.properties
```

- `spring.cloud.nacos.config.shared-dataids`参数用来配置多个共享配置的`Data Id`，多个的时候用用逗号分隔
- `spring.cloud.nacos.config.refreshable-dataids`参数用来定义哪些共享配置的`Data Id`在配置变化时，应用中可以动态刷新，多个`Data Id`之间用逗号隔开。如果没有明确配置，默认情况下所有共享配置都不支持动态刷新

## 配置加载的优先级

当我们加载多个配置的时候，如果存在相同的key时，我们需要深入了解配置加载的优先级关系。

在使用Nacos配置的时候，主要有以下三类配置：

- A: 通过`spring.cloud.nacos.config.shared-dataids`定义的共享配置
- B: 通过`spring.cloud.nacos.config.ext-config[n]`定义的加载配置
- C: 通过内部规则（`spring.cloud.nacos.config.prefix`、`spring.cloud.nacos.config.file-extension`、`spring.cloud.nacos.config.group`这几个参数）拼接出来的配置

要弄清楚这几个配置加载的顺序，我们从日志中也可以很清晰的看到，我们可以做一个简单的实验：

```properties
spring.cloud.nacos.config.ext-config[0].data-id=a.properties
spring.cloud.nacos.config.ext-config[0].group=DEFAULT_GROUP
spring.cloud.nacos.config.ext-config[0].refresh=true

spring.cloud.nacos.config.shared-dataids=b.properties
spring.cloud.nacos.config.refreshable-dataids=b.properties
```

这个配置文件的加载顺寻是 A < B < C 

# Nacos的数据持久化

在搭建Nacos集群之前，我们需要先修改Nacos的数据持久化配置为MySQL存储。默认情况下，Nacos使用嵌入式数据库实现数据的存储。所以，如果启动多个默认配置下的Nacos节点，数据存储是存在一致性问题的。为了解决这个问题，Nacos采用了集中式存储的方式来支持集群化部署，目前只要支持MySQL的存储。

配置Nacos的MySQL存储只需要下面三步：

**第一步**：安装数据库，版本要求：5.6.5+

**第二步**：初始化MySQL数据库，数据库初始化文件：`nacos-mysql.sql`，该文件可以在Nacos程序包下的`conf`目录下获得。

 **第三步**：修改`conf/application.properties`文件，增加支持MySQL数据源配置，添加（目前只支持mysql）数据源的url、用户名和密码。配置样例如下： 

```properties
spring.datasource.platform=mysql

db.num=1
db.url.0=jdbc:mysql://localhost:3306/nacos?characterEncoding=utf8&connectTimeout=1000&socketTimeout=3000&autoReconnect=true
db.user=root
db.password=
```

#### 集群配置

在Nacos的`conf`目录下有一个`cluster.conf.example`，可以直接把`example`扩展名去掉来使用，也可以单独创建一个`cluster.conf`文件，然后打开将后续要部署的Nacos实例地址配置在这里。

本文以在本地不同端点启动3个Nacos服务端为例，可以如下配置

```
127.0.0.1:8841
127.0.0.1:8842
127.0.0.1:8843
```

 在完成了上面的配置之后，我们就可以开始在各个节点上启动Nacos实例，以组建Nacos集群来使用了。 

本文中，在集群配置的时候，我们设定了3个Nacos的实例都在本地，只是以不同的端口区分，所以我们在启动Nacos的时候，需要修改不同的端口号。

下面介绍一种方法来方便地启动Nacos的三个本地实例，我们可以将bin目录下的`startup.sh`脚本复制三份，分别用来启动三个不同端口的Nacos实例，为了可以方便区分不同实例的启动脚本，我们可以把端口号加入到脚本的命名中，比如：

- startup-8841.sh
- startup-8842.sh
- startup-8843.sh

 然后，分别修改这三个脚本中的参数，具体如下图的红色部分（端口号根据上面脚本命名分配）： 

![](C:\Program Files\blog\source\_posts\spring-cloud-aliba-服务注册\sh.png)

#### Proxy配置

在Nacos的集群启动完毕之后，根据架构图所示，我们还需要提供一个统一的入口给我们用来维护以及给Spring Cloud应用访问。简单地说，就是我们需要为上面启动的的三个Nacos实例做一个可以为它们实现负载均衡的访问点。这个实现的方式非常多，这里就举个用Nginx来实现的简单例子吧。

在Nginx配置文件的http段中，我们可以加入下面的配置内容：

![](C:\Program Files\blog\source\_posts\spring-cloud-aliba-服务注册\nginx.png)