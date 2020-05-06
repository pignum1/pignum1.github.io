---
title: spring-cloud-hystrix
date: 2019-11-12 22:40:35
tags: [hystrix,spring cloud ]
type: "categories"
categories: spring cloud
---

# Hystrix

 		在分布式环境中，许多服务依赖项中的一些必然会失败。Hystrix是一个库，通过添加延迟容忍和容错逻辑，帮助你控制这些分布式服务之间的交互。Hystrix通过隔离服务之间的访问点、停止级联失败和提供回退选项来实现这一点，所有这些都可以提高系统的整体弹性 

## Hystrix的设计目的

1. 对通过第三方客户端库访问的依赖项（通常是通过网络）的延迟和故障进行保护和控制。
2. 在复杂的分布式系统中阻止级联故障。
3. 快速失败，快速恢复。
4. 回退，尽可能优雅地降级。
5. 启用近实时监控、警报和操作控制。

​		复杂分布式体系结构中的应用程序有许多依赖项，每个依赖项在某些时候都不可避免地会失败。如果主机应用程序没有与这些外部故障隔离，那么它有可能被他们拖垮。

## Hystrix设计原则

- 防止任何单个依赖项耗尽所有容器（如Tomcat）用户线程。
- 甩掉包袱，快速失败而不是排队。
- 在任何可行的地方提供回退，以保护用户不受失败的影响。
- 使用隔离技术（如隔离板、泳道和断路器模式）来限制任何一个依赖项的影响。
- 通过近实时的度量、监视和警报来优化发现时间。
- 通过配置的低延迟传播来优化恢复时间。
- 支持对Hystrix的大多数方面的动态属性更改，允许使用低延迟反馈循环进行实时操作修改。
- 避免在整个依赖客户端执行中出现故障，而不仅仅是在网络流量中。

## Hystrix是如何实现它的目标的

1. 用一个HystrixCommand 或者 HystrixObservableCommand （这是命令模式的一个例子）包装所有的对外部系统（或者依赖）的调用，典型地它们在一个单独的线程中执行
2. 调用超时时间比你自己定义的阈值要长。有一个默认值，对于大多数的依赖项你是可以自定义超时时间的。
3. 为每个依赖项维护一个小的线程池(或信号量)；如果线程池满了，那么该依赖性将会立即拒绝请求，而不是排队。
4. 调用的结果有这么几种：成功、失败（客户端抛出异常）、超时、拒绝。
5. 在一段时间内，如果服务的错误百分比超过了一个阈值，就会触发一个断路器来停止对特定服务的所有请求，无论是手动的还是自动的。
6. 当请求失败、被拒绝、超时或短路时，执行回退逻辑。
7. 近实时监控指标和配置变化。

 当你使用Hystrix来包装每个依赖项时，上图中所示的架构会发生变化，如下图所示： 

 每个依赖项相互隔离，当延迟发生时，它会被限制在资源中，并包含回退逻辑，该逻辑决定在依赖项中发生任何类型的故障时应作出何种响应： 

![](depence.png)



# Hystrix的使用

## 服务容错保护（Hystrix服务降级）

 使用Spring Cloud Hystrix实现断路器 

创建两个spring cloud服务，一个服务方，一个调用方，在调用方中添加断路器的依赖

```groovy
implementation 'org.springframework.cloud:spring-cloud-starter-netflix-hystrix'
```

创建服务提供方 Hystrix-demo1，创建测试方法，添加线程睡眠5秒来触发断路器

```java
@RestController
public class HelloController {
    @GetMapping("/hello")
    public String dc() {
        try {
            Thread.sleep( 50000 );
            return "wake";
        }catch (Exception e){
            return  "sleep";
        }
    }
}
```

创建调用方  Hystrix-demo2，

在启动类商添加注解来启用断路器

```java
@EnableCircuitBreaker
@EnableDiscoveryClient
@SpringBootApplication
```

测试请求方法， API方法加上了@HystrixCommand注解，并设置fallbackMethod属性为回退方法名称 

```java
@RestController
public class consumerController {

    @Autowired
    RestTemplate restTemplate;

    @GetMapping("/consumer")
    @HystrixCommand(fallbackMethod = "fallback")
    public String consumer() {
        return restTemplate.getForObject("http://hystrix-demo1/hello", String.class);
    }

    public String fallback() {
        return "fallback";
    }

}
```

分别启动服务提供者和服务消费者，并用POSTMAN 调用consumer方法，此时页面返回的数据为

![](down.png)

 		以看到服务提供方输出了原本要返回的结果，但是由于返回前延迟了5秒，而服务消费方触发了服务请求超时异常，服务消费者就通过HystrixCommand注解中指定的降级逻辑进行执行，因此该请求的结果返回了`fallback`。这样的机制，对自身服务起到了基础的保护，同时还为异常情况提供了自动的服务降级切换机制。 

## 依赖隔离

 	而Hystrix使用该模式实现线程池的隔离，它会为每一个Hystrix命令创建一个独立的线程池，这样就算某个在Hystrix命令包装下的依赖服务出现延迟过高的情况，也只是对该依赖服务的调用产生影响，而不会拖慢其他的服务。 

- 应用自身得到完全的保护，不会受不可控的依赖服务影响。即便给依赖服务分配的线程池被填满，也不会影响应用自身的额其余部分。
- 可以有效的降低接入新服务的风险。如果新服务接入后运行不稳定或存在问题，完全不会影响到应用其他的请求。
- 当依赖的服务从失效恢复正常后，它的线程池会被清理并且能够马上恢复健康的服务，相比之下容器级别的清理恢复速度要慢得多。
- 当依赖的服务出现配置错误的时候，线程池会快速的反应出此问题（通过失败次数、延迟、超时、拒绝等指标的增加情况）。同时，我们可以在不影响应用功能的情况下通过实时的动态属性刷新（后续会通过Spring Cloud Config与Spring Cloud Bus的联合使用来介绍）来处理它。
- 当依赖的服务因实现机制调整等原因造成其性能出现很大变化的时候，此时线程池的监控指标信息会反映出这样的变化。同时，我们也可以通过实时动态刷新自身应用对依赖服务的阈值进行调整以适应依赖方的改变。
- 除了上面通过线程池隔离服务发挥的优点之外，每个专有线程池都提供了内置的并发实现，可以利用它为同步的依赖服务构建异步的访问。

 我们使用了@HystrixCommand来将某个函数包装成了Hystrix命令，这里除了定义服务降级之外，Hystrix框架就会自动的为这个函数实现调用的隔离。所以，依赖隔离、服务降级在使用时候都是一体化实现的，这样利用Hystrix来实现服务容错保护在编程模型上就非常方便的，并且考虑更为全面。 

## 断路器

 “断路器”本身是一种开关装置，用于在电路上保护线路过载，当线路中有电器发生短路时，“断路器”能够及时的切断故障电路，  分布式架构中，断路器模式的作用也是类似的，当某个服务单元发生故障（类似用电器发生短路）之后，通过断路器的故障监控（类似熔断保险丝），直接切断原来的主逻辑调用。 

 那么断路器是在什么情况下开始起作用呢？这里涉及到断路器的三个重要参数：快照时间窗、请求总数下限、错误百分比下限 

- 快照时间窗：断路器确定是否打开需要统计一些请求和错误数据，而统计的时间范围就是快照时间窗，默认为最近的10秒。
- 请求总数下限：在快照时间窗内，必须满足请求总数下限才有资格根据熔断。默认为20，意味着在10秒内，如果该hystrix命令的调用此时不足20次，即时所有的请求都超时或其他原因失败，断路器都不会打开。
- 错误百分比下限：当请求总数在快照时间窗内超过了下限，比如发生了30次调用，如果在这30次调用中，有16次发生了超时异常，也就是超过50%的错误百分比，在默认设定50%下限情况下，这时候就会将断路器打开。

 在断路器打开之后，处理逻辑并没有结束，我们的降级逻辑已经被成了主逻辑，那么原来的主逻辑要如何恢复呢？对于这一问题，hystrix也为我们实现了自动恢复功能。当断路器打开，对主逻辑进行熔断之后，hystrix会启动一个休眠时间窗，在这个时间窗内，降级逻辑是临时的成为主逻辑，当休眠时间窗到期，断路器将进入半开状态，释放一次请求到原来的主逻辑上，如果此次请求正常返回，那么断路器将继续闭合，主逻辑恢复，如果这次请求依然有问题，断路器继续进入打开状态，休眠时间窗重新计时。 

# Hystrix监控面板

 断路器是根据一段时间窗内的请求情况来判断并操作断路器的打开和关闭状态的。而这些请求情况的指标信息都是HystrixCommand和HystrixObservableCommand实例在执行过程中记录的重要度量信息，它们除了Hystrix断路器实现中使用之外，对于系统运维也有非常大的帮助。 

 下面我们基于之前的示例来结合Hystrix Dashboard实现Hystrix指标数据的可视化面板， 我们将用到的几个应用  

- cloud-eureka-server：服务注册中心
-  Hystrix-demo1：服务提供者
-  Hystrix-demo2：使服务消费者

 创建一个标准的Spring Boot工程，命名为：hystrix-dashboard ,添加依赖

```groovy
	implementation 'org.springframework.boot:spring-boot-starter-actuator'
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-hystrix'
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-hystrix-dashboard'
```

在启动类上添加注解

```java
@EnableHystrixDashboard
@SpringBootApplication
public class HystrixDashboardApplication {

	public static void main(String[] args) {
		SpringApplication.run(HystrixDashboardApplication.class, args);
	}

}
```

添加配置文件

```properties
spring.application.name=hystrix-dashboard
server.port=1301
```

启动项目后访问  http://localhost:1301/hystrix ，显示页面如下

![](hystrix.png)

这是Hystrix Dashboard的监控首页，该页面中并没有具体的监控信息。从页面的文字内容中我们可以知道，Hystrix Dashboard共支持三种不同的监控方式，依次为：

- 默认的集群监控：通过URL`http://turbine-h；ostname:port/turbine.stream`开启，实现对默认集群的监控。
- 指定的集群监控：通过URL`http://turbine-hostname:port/turbine.stream?cluster=[clusterName]`开启，实现对clusterName集群的监控。
- 单体应用的监控：通过URL`http://hystrix-app:port/hystrix.stream`开启，实现对具体某个服务实例的监控。

前两者都对集群的监控，需要整合Turbine才能实现，我们主要实现对单个服务实例的监控，所以这里我们先来实现**单个服务实例**的监控。

既然Hystrix Dashboard监控单实例节点需要通过访问实例的`/hystrix.stream`接口来实现，自然我们需要为服务实例添加这个端点，而添加该功能的步骤也同样简单。



## **单个服务实例**的监控

 Hystrix Dashboard 监控的结构

![](springcloud-hystrix\struct.png)



在**服务消费者**（Hystrix-demo2）实例中添加监听配置

```groovy
implementation 'org.springframework.cloud:spring-cloud-starter-netflix-hystrix'implementation 'org.springframework.boot:spring-boot-starter-actuator'
```

添加配置文件

 ```properties

#为服务实例（被监控服务）添加这个 endpoint，修改服务实例的配置文件，添加对actuator的配置
management.endpoints.web.exposure.include=hystrix.stream

#修改Hystrix默认超时时间
hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds = 2000
 ```

在启动类种添加

```java
@Bean
public ServletRegistrationBean hystrixMetricsStreamServlet() {
    ServletRegistrationBean registration = new ServletRegistrationBean(new HystrixMetricsStreamServlet());
    registration.addUrlMappings("/hystrix.stream");
    return registration;
}
```

此时在 http://localhost:1301/hystrix  输入框中输入http://:服务消费者IP:服务消费端口/hystrix.stream，

这个时候页面显示的是Loading,发起服务容错种的consumer请求，页面上![](hystrixScreen.png)

显示的各个参数解释引用别人的图![](hystrixParams.png)

 这里就对单体服务的监控介绍完了。但是在分布式系统中往往有很多服务需要监控。

 *注意：当使用Hystrix Dashboard监控Spring Cloud Zuul构建的API网关时，ThreadPool信息会一直处于Loading状态，这是由于Zuul默认使用信号量来实现隔离，只有通过Hystrix配置把隔离机制改为线程池的方式才能得以展示。* 

# Hystrix监控数据聚合

​		通过Hystrix Dashboard，我们可以方便的查看服务实例的综合情况，比如：服务调用次数、服务调用延迟等。但是仅通过Hystrix Dashboard我们只能实现对服务当个实例的数据展现，在生产环境我们的服务是肯定需要做高可用的，那么对于多实例的情况，我们就需要将这些度量指标数据进行聚合。下面我们就来介绍一下另外一个工具：Turbine。 

​	上文中构建的有

- eureka-server：服务注册中心
- Hystrix-demo1：服务提供者
- Hystrix-demo1：使用ribbon和hystrix实现的服务消费者
- hystrix-dashboard：用于展示`eureka-consumer-ribbon-hystrix`服务的Hystrix数据

### 通过HTTP收集聚合（turbine检测单个集群 ）

创建一个新的 Spring Boot工程，命名为：turbine 

添加依赖和properties的配置

```groovy
	implementation 'org.springframework.boot:spring-boot-starter-web'

	implementation 'org.springframework.boot:spring-boot-starter-actuator'
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-hystrix'
//	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-turbine-stream'

	// https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-turbine
	compile group: 'org.springframework.cloud', name: 'spring-cloud-starter-turbine', version: '1.4.7.RELEASE'
// https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-eureka
	compile group: 'org.springframework.cloud', name: 'spring-cloud-starter-eureka', version: '1.4.7.RELEASE'

```

```properties
spring.application.name=turbine

server.port=8989

management.server.port=8990

eureka.client.serviceUrl.defaultZone=http://localhost:5678/eureka/

#turbine.app-config参数指定了需要收集监控信息的服务名,这里监测的服务消费者，多个,隔开
turbine.app-config=Hystrix-demo2 

#参数指定了集群名称为default，当我们服务数量非常多的时候，可以启动多个Turbine服务来构建不同的聚合集群，而该参数可以用来区分这些不同的聚合集群，
# 同时该参数值可以在Hystrix仪表盘中用来定位不同的聚合集群，只需要在Hystrix Stream的URL中通过cluster参数来指定；
turbine.cluster-name-expression="default"

#eureka.instance.hostname= mymaster
#eureka.instance.prefer-ip-address=false

#参数设置为true，可以让同一主机上的服务通过主机名与端口号的组合来进行区分，
# 默认情况下会以host来区分不同的服务，这会使得在本地调试的时候，本机上的不同服务聚合成一个服务来统计
turbine.combine-host-port=true
```

在启动类上添加

```java
@EnableTurbine
@SpringBootApplication
public class TurbineApplication {
	public static void main(String[] args) {
		SpringApplication.run(TurbineApplication.class, args);
	}
}
```

此时再启动turbine 服务，再在 http://localhost:1301/hystrix  输入turbine 的http://localhost:8989/turbine.stream，这时候页面上还是Loading,再访问一次消费者的consumer端口 http://localhost:5888/consumer 

![](single.png)

这格式化系统的架构如下图

![](singleStruct.png) 

### 通过消息代理收集聚合（AMQP）

 pring Cloud在封装Turbine的时候，还实现了基于消息代理的收集实现。所以，我们可以将所有需要收集的监控信息都输出到消息代理中，然后Turbine服务再从消息代理中异步的获取这些监控信息，最后将这些监控信息聚合并输出到Hystrix Dashboard中。通过引入消息代理，我们的Turbine和Hystrix Dashoard实现的监控架构可以改成如下图所示的结构： 

![](t-ampq.png)

这块等我整理完rabbitmq在回来

