---
title: spring-cloud 服务网关
date: 2019-11-26 01:00:29
tags: [zuul,spring cloud ]
type: "categories"
categories: spring cloud
---

# 服务网关

 之前几篇Spring Cloud中几个核心组件的介绍，我们已经可以构建一个简略的（不够完善）微服务架构了。比如下图所示： 

![](struct.png)

 我们使用Spring Cloud Netflix中的Eureka实现了服务注册中心以及服务注册与发现；而服务间通过Ribbon或Feign实现服务的消费以及均衡负载；通过Spring Cloud Config实现了应用多环境的外部化配置以及版本管理。为了使得服务集群更为健壮，使用Hystrix的融断机制来避免在微服务架构中个别服务出现异常时引起的故障蔓延。 

 在该架构中，我们的服务集群包含：内部服务Service A和Service B，他们都会注册与订阅服务至Eureka Server，而Open Service是一个对外的服务，通过均衡负载公开至服务调用方。 

- 首先，破坏了服务无状态特点。为了保证对外服务的安全性，我们需要实现对服务访问的权限控制，而开放服务的权限控制机制将会贯穿并污染整个开放服务的业务逻辑，这会带来的最直接问题是，破坏了服务集群中REST API无状态的特点。从具体开发和测试的角度来说，在工作中除了要考虑实际的业务逻辑之外，还需要额外可续对接口访问的控制处理。
- 其次，无法直接复用既有接口。当我们需要对一个即有的集群内访问接口，实现外部服务访问时，我们不得不通过在原有接口上增加校验逻辑，或增加一个代理调用来实现权限控制，无法直接复用原有的接口。

 为了解决上面这些问题，我们需要将权限控制这样的东西从我们的服务单元中抽离出去，而最适合这些逻辑的地方就是处于对外访问最前端的地方，我们需要一个更强大一些的均衡负载器，它就是本文将来介绍的：服务网关。 

 		服务网关是微服务架构中一个不可或缺的部分。通过服务网关统一向外系统提供REST API的过程中，除了具备服务路由、均衡负载功能之外，它还具备了权限控制等功能。Spring Cloud Netflix中的Zuul就担任了这样的一个角色，为微服务架构提供了前门保护的作用，同时将权限控制这些较重的非业务逻辑内容迁移到服务路由层面，使得服务集群主体能够具备更高的可复用性和可测试性。 



## 构建服务网关

 Spring Cloud Zuul来构建服务网关 

添加服务网关的依赖

```groovy
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-server'
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-zuul'
```

在启动类上添加服务网关注解

```java
@EnableZuulProxy
@SpringBootApplication
@EnableEurekaClient
public class ApiGatewayApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApiGatewayApplication.class, args);
	}	
}
```

修改配置文件application.properties

```properties
# 基础信息配置
spring.application.name=api-gateway
server.port=5679

# 路由规则配置
#zuul.routes.api-a.path=/demo/**
#zuul.routes.api-a.serviceId=practice
zuul.routes.ribbon-1=/mypath/**

# API网关也将作为一个服务注册到eureka-server上
eureka.client.service-url.defaultZone=http://localhost:5678/eureka/

#注册中心上ip地址显示
eureka.instance.prefer-ip-address=true
eureka.instance.instance-id=${spring.cloud.client.ipAddress}:${server.port}

#设置服务注销事件(秒)
eureka.instance.lease-renewal-interval-in-seconds=5
eureka.instance.lease-expiration-duration-in-seconds=10
```

启动服务注册中心 eureka-service,服务消费则ribbon-1 ,服务网关api-gateway ,直接请求Hystrix-demo1的路径是localhost:5888/consumer，通过网关调用时，路劲可以写成 localhosy:5679/ribbon-1/consumer

## 路由配置

###  传统路由配置

 所谓的传统路由配置方式就是在不依赖于服务发现机制的情况下，通过在配置文件中具体指定每个路由表达式与服务实例的映射关系来实现API网关对外部请求的路由。 

 单实例配置：通过一组`zuul.routes..path`与`zuul.routes..url`参数对的方式配置，比如： 

```properties
zuul.routes.user-service.path=/user-service/**
zuul.routes.user-service.url=http://localhost:8080/
```

 该配置实现了对符合`/user-service/**`规则的请求路径转发到`http://localhost:8080/`地址的路由规则，比如，当有一个请求`http://localhost:5679/user-service/hello`被发送到API网关上，由于`/user-service/hello`能够被上述配置的`path`规则匹配，所以API网关会转发请求到`http://localhost:8080/hello`地址。 

 多实例配置：通过一组`zuul.routes..path`与`zuul.routes..serviceId`参数对的方式配置，比如： 

```properties
zuul.routes.user-service.path=/user-service/**
zuul.routes.user-service.serviceId=user-service

ribbon.eureka.enabled=false
user-service.ribbon.listOfServers=http://localhost:8080/,http://localhost:8081/
```

该配置实现了对符合`/user-service/**`规则的请求路径转发到`http://localhost:8080/`和`http://localhost:8081/`两个实例地址的路由规则。它的配置方式与服务路由的配置方式一样，都采用了`zuul.routes..path`与`zuul.routes..serviceId`参数对的映射方式，只是这里的`serviceId`是由用户手工命名的服务名称，配合`.ribbon.listOfServers`参数实现服务与实例的维护。由于存在多个实例，API网关在进行路由转发时需要实现负载均衡策略，于是这里还需要Spring Cloud Ribbon的配合。由于在Spring Cloud Zuul中自带了对Ribbon的依赖，所以我们只需要做一些配置即可，比如上面示例中关于Ribbon的各个配置，它们的具体作用如下：

- `ribbon.eureka.enabled`：由于`zuul.routes..serviceId`指定的是服务名称，默认情况下Ribbon会根据服务发现机制来获取配置服务名对应的实例清单。但是，该示例并没有整合类似Eureka之类的服务治理框架，所以需要将该参数设置为false，不然配置的`serviceId`是获取不到对应实例清单的。
- `user-service.ribbon.listOfServers`：该参数内容与`zuul.routes..serviceId`的配置相对应，开头的`user-service`对应了`serviceId`的值，这两个参数的配置相当于在该应用内部手工维护了服务与实例的对应关系。

不论是单实例还是多实例的配置方式，我们都需要为每一对映射关系指定一个名称，也就是上面配置中的``，每一个``就对应了一条路由规则。每条路由规则都需要通过`path`属性来定义一个用来匹配客户端请求的路径表达式，并通过`url`或`serviceId`属性来指定请求表达式映射具体实例地址或服务名。

### 服务路由配置

服务路由我们在上一篇中也已经有过基础的介绍和体验，Spring Cloud Zuul通过与Spring Cloud Eureka的整合，实现了对服务实例的自动化维护，所以在使用服务路由配置的时候，我们不需要向传统路由配置方式那样为`serviceId`去指定具体的服务实例地址，只需要通过一组`zuul.routes..path`与`zuul.routes..serviceId`参数对的方式配置即可。

比如下面的示例，它实现了对符合`/user-service/**`规则的请求路径转发到名为`user-service`的服务实例上去的路由规则。其中``可以指定为任意的路由名称。

```properties
zuul.routes.user-service.path=/user-service/**
zuul.routes.user-service.serviceId=user-service
```

 对于面向服务的路由配置，除了使用`path`与`serviceId`映射的配置方式之外，还有一种更简洁的配置方式：`zuul.routes.=`，其中``用来指定路由的具体服务名，``用来配置匹配的请求表达式。比如下面的例子，它的路由规则等价于上面通过`path`与`serviceId`组合使用的配置方式。 

```properties
zuul.routes.user-service=/user-service/**
```

 传统路由的映射方式比较直观且容易理解，API网关直接根据请求的URL路径找到最匹配的`path`表达式，直接转发给该表达式对应的`url`或对应`serviceId`下配置的实例地址，以实现外部请求的路由。那么当采用`path`与`serviceId`以服务路由方式实现时候，没有配置任何实例地址的情况下，外部请求经过API网关的时候，它是如何被解析并转发到服务具体实例的呢？ 

 在Spring Cloud Netflix中，Zuul巧妙的整合了Eureka来实现面向服务的路由。实际上，我们可以直接将API网关也看做是Eureka服务治理下的一个普通微服务应用。它除了会将自己注册到Eureka服务注册中心上之外，也会从注册中心获取所有服务以及它们的实例清单。所以，在Eureka的帮助下，API网关服务本身就已经维护了系统中所有serviceId与实例地址的映射关系。当有外部请求到达API网关的时候，根据请求的URL路径找到最佳匹配的`path`规则，API网关就可以知道要将该请求路由到哪个具体的`serviceId`上去。 

## 过滤器示例

 通过上面所述的两篇我们，我们已经能够实现请求的路由功能，所以我们的微服务应用提供的接口就可以通过统一的API网关入口被客户端访问到了。但是，每个客户端用户请求微服务应用提供的接口时，它们的访问权限往往都需要有一定的限制，系统并不会将所有的微服务接口都对它们开放。然而，目前的服务路由并没有限制权限这样的功能，所有请求都会被毫无保留地转发到具体的应用并返回结果，为了实现对客户端请求的安全校验和权限控制，最简单和粗暴的方法就是为每个微服务应用都实现一套用于校验签名和鉴别权限的过滤器或拦截器。不过，这样的做法并不可取，它会增加日后的系统维护难度，因为同一个系统中的各种校验逻辑很多情况下都是大致相同或类似的，这样的实现方式会使得相似的校验逻辑代码被分散到了各个微服务中去，冗余代码的出现是我们不希望看到的。所以，比较好的做法是将这些校验逻辑剥离出去，构建出一个独立的鉴权服务。在完成了剥离之后，有不少开发者会直接在微服务应用中通过调用鉴权服务来实现校验，但是这样的做法仅仅只是解决了鉴权逻辑的分离，并没有在本质上将这部分不属于业余的逻辑拆分出原有的微服务应用，冗余的拦截器或过滤器依然会存在。 

由于网关服务的加入，外部客户端访问我们的系统已经有了统一入口，既然这些校验与具体业务无关，那何不在请求到达的时候就完成校验和过滤，而不是转发后再过滤而导致更长的请求延迟。同时，通过在网关中完成校验和过滤，微服务应用端就可以去除各种复杂的过滤器和拦截器了，这使得微服务应用的接口开发和测试复杂度也得到了相应的降低。

为了在API网关中实现对客户端请求的校验，我们将需要使用到Spring Cloud Zuul的另外一个核心功能：**过滤器**。

 我们定义了一个简单的Zuul过滤器，它实现了在请求被路由之前检查HttpServletRequest中是否有login参数，若有就进行路由，若没有就拒绝访问，返回401 Unauthorized错误。 

```java
public class ZuulFilter extends com.netflix.zuul.ZuulFilter {
    /**
     *
     * fileType的返回值类型表示为过滤器的类型，过滤器的类型表示在那个生命周期执行
     * pre,post,error,route,static
     * pre表示的是在路由之前执行
     * @return
     */
    @Override
    public String filterType() {
        return "pre";
    }

    /**
     * 表示过滤器的执行顺序（多个过滤器时有意义）
     * @return
     */
    @Override
    public int filterOrder() {
        return 0;
    }

    /**
     *表示过滤器是否执行
     * @return
     */
    @Override
    public boolean shouldFilter() {
        return true;
    }

    /**
     * 具体的过滤规则
     * @return
     */
    @Override
    public Object run() {

        RequestContext ctx = RequestContext.getCurrentContext();
        HttpServletRequest request = ctx.getRequest();
        String login = request.getParameter( "login" );
        if(login == null){
            ctx.setSendZuulResponse(false);
            ctx.setResponseStatusCode(401);
            ctx.addZuulResponseHeader("content-type","text/html;charset=utf-8");
            ctx.setResponseBody("无登陆信息");
        }
        return null;
    }
}
```

 在实现了自定义过滤器之后，它并不会直接生效，我们还需要为其创建具体的Bean才能启动该过滤器，比如，在应用主类中增加如下内容 ,

```java
@EnableZuulProxy
@SpringBootApplication
@EnableEurekaClient
public class ApiGatewayApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApiGatewayApplication.class, args);
	}
	@Bean
	ZuulFilter getZuulFilter() {
		return new ZuulFilter();
	}
}
```

重新启动服务网关，再次访问 http://localhost:5679/mypath/consumer ,页面显示

![](gate.png)

这个时候通过网关必须携带login的信息  http://localhost:5679/mypath/consumer?login=2 

 到这里，对于Spring Cloud Zuul过滤器的基本功能就已介绍完毕。 

## zuul核心过滤器源码分析

 包含了对请求的路由和过滤两个功能，其中路由功能负责将外部请求转发到具体的微服务实例上，是实现外部访问统一入口的基础；而过滤器功能则负责对请求的处理过程进行干预，是实现请求校验、服务聚合等功能的基础。然而实际上，路由功能在真正运行时，它的路由映射和请求转发都是由几个不同的过滤器完成的。其中，路由映射主要通过pre类型的过滤器完成，它将请求路径与配置的路由规则进行匹配，以找到需要转发的目标地址；而请求转发的部分则是由route类型的过滤器来完成，对pre类型过滤器获得的路由地址进行转发。所以，过滤器可以说是Zuul实现API网关功能最为核心的部件，每一个进入Zuul的HTTP请求都会经过一系列的过滤器处理链得到请求响应并返回给客户端。 

 Spring Cloud Zuul中实现的过滤器必须包含4个基本特征：过滤类型、执行顺序、执行条件、具体操作。这些元素看着似乎非常的熟悉，实际上它就是ZuulFilter接口中定义的四个抽象方法： 

```java
String filterType();
    
int filterOrder();
    
boolean shouldFilter();
    
Object run();
```

- filterType：该函数需要返回一个字符串来代表过滤器的类型，而这个类型就是在HTTP请求过程中定义的各个阶段。在Zuul中默认定义了四种不同生命周期的过滤器类型，具体如下：
  - pre：可以在请求被路由之前调用。
  - routing：在路由请求时候被调用。
  - post：在routing和error过滤器之后被调用。
  - error：处理请求时发生错误时被调用。
- filterOrder：通过int值来定义过滤器的执行顺序，数值越小优先级越高。
- shouldFilter：返回一个boolean类型来判断该过滤器是否要执行。我们可以通过此方法来指定过滤器的有效范围。
- run：过滤器的具体逻辑。在该函数中，我们可以实现自定义的过滤逻辑，来确定是否要拦截当前的请求，不对其进行后续的路由，或是在请求路由返回结果之后，对处理结果做一些加工等。

## 请求生命周期

 	Zuul默认定义了四个不同的过滤器类型，它们覆盖了一个外部HTTP请求到达API网关，直到返回请求结果的全部生命周期。下图源自Zuul的官方WIKI中关于请求生命周期的图解，它描述了一个HTTP请求到达API网关之后，如何在各个不同类型的过滤器之间流转的详细过程。 

![](lifeCycle.png)

 当外部HTTP请求到达API网关服务的时候，首先它会进入第一个阶段pre，在这里它会被pre类型的过滤器进行处理，该类型的过滤器主要目的是在进行请求路由之前做一些前置加工，比如请求的校验等。在完成了pre类型的过滤器处理之后，请求进入第二个阶段routing，也就是之前说的路由请求转发阶段，请求将会被routing类型过滤器处理，这里的具体处理内容就是将外部请求转发到具体服务实例上去的过程，当服务实例将请求结果都返回之后，routing阶段完成，请求进入第三个阶段post，此时请求将会被post类型的过滤器进行处理，这些过滤器在处理的时候不仅可以获取到请求信息，还能获取到服务实例的返回信息，所以在post类型的过滤器中，我们可以对处理结果进行一些加工或转换等内容。另外，还有一个特殊的阶段error，该阶段只有在上述三个阶段中发生异常的时候才会触发，但是它的最后流向还是post类型的过滤器，因为它需要通过post过滤器将最终结果返回给请求客户端。 