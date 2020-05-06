---
title: spring cloud 集成练习项目
date: 2019-12-15 12:52:39
tags: [,spring cloud ]
type: "categories"
categories: spring cloud
---

# 创建服务注册中心 （eureka）

环境配置:

JDK 1.8

spring cloud version:Greenwich.SR1

spring boot version:2.1.5.RELEASE

eureka-server作为服务发现的核心，第一个搭建，后面的服务都要注册到eureka-server上，意思是告诉eureka-server自己的服务地址是啥。当然还可以用zookeeper或者spring consul。

这里我用的gradle构建的项目，再build.gradle中添加依赖

```groovy
plugins {
	id 'org.springframework.boot' version '2.2.2.RELEASE'
	id 'io.spring.dependency-management' version '1.0.8.RELEASE'
	id 'java'
}

apply plugin: 'java'
apply plugin: 'idea'
group = 'com.example'
version = '0.0.3'
sourceCompatibility = '1.8'

repositories {
	mavenCentral()
//	maven { url "http://maven.aliyun.com/nexus/content/groups/public/" }
}

ext {
	set('springCloudVersion', "Hoxton.RELEASE")
}

dependencies {
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-server'
	compile('org.springframework.boot:spring-boot-starter-security')
	testImplementation('org.springframework.boot:spring-boot-starter-test') {
		exclude group: 'org.junit.vintage', module: 'junit-vintage-engine'
	}
}

dependencyManagement {
	imports {
		mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
	}
}

test {
	useJUnitPlatform()
}

jar {
    String someString = ''
    configurations.runtime.each { someString = someString + " lib\\" + it.name }
    manifest {
        attributes 'Main-Class': 'com.each.dubboMainEnd'
        attributes 'Class-Path': someString
    }
}

task copyJar(type:Copy){
    from configurations.runtime
    into ('build/libs/lib')

}

task release(type: Copy,dependsOn: [build,copyJar]) {
//    from  'conf'
    //   into ('build/libs/eachend/conf')
}
```

在resurce下的application.properties修改配置文件

```properties
server.port=5678
spring.security.user.roles=SUPERUSER
spring.security.user.name=wxy
spring.security.user.password=wxy123
eureka.client.register-with-eureka=false
eureka.client.fetch-registry=false
eureka.instance.hostname=localhost
eureka.client.serviceUrl.defaultZone=http://wxy:wxy123@localhost:5678/eureka
```

在启动类上添加注解

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@EnableEurekaServer //启动服务注册中心
@SpringBootApplication
public class CloudEurekaServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(CloudEurekaServiceApplication.class, args);

	}

}
```

启动服务，访问http://localhost:5678/，出现登陆页面，输入账号密码，就可以访问到注册中心

# 创建config-server分布式配置中心服务（git版）

首先要准备一个[git仓库](https://github.com/pignum1/config),然后新建一个springboot项目，修改build.gradle

```groovy
plugins {
	id 'org.springframework.boot' version '2.2.2.RELEASE'
	id 'io.spring.dependency-management' version '1.0.8.RELEASE'
	id 'java'
}

apply plugin: 'java'
apply plugin: 'idea'

group = 'com.example'
version = '0.0.4'
sourceCompatibility = '1.8'

repositories {
	mavenCentral()
}

ext {
	set('springCloudVersion', "Hoxton.SR1")
}

dependencies {
	implementation 'org.springframework.cloud:spring-cloud-config-server'
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
//	implementation 'org.springframework.cloud:spring-cloud-starter-security'
	compile('org.springframework.boot:spring-boot-starter-security')

	compile('org.springframework.boot:spring-boot-starter-actuator')
	testImplementation('org.springframework.boot:spring-boot-starter-test') {
		exclude group: 'org.junit.vintage', module: 'junit-vintage-engine'
	}
}

dependencyManagement {
	imports {
		mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
	}
}

test {
	useJUnitPlatform()
}

jar {
	String someString = ''
	configurations.runtime.each { someString = someString + " lib\\" + it.name }
	manifest {
		attributes 'Main-Class': 'com.each.dubboMainEnd'
		attributes 'Class-Path': someString
	}
}

task copyJar(type:Copy){
	from configurations.runtime
	into ('build/libs/lib')

}

task release(type: Copy,dependsOn: [build,copyJar]) {
//    from  'conf'
	//   into ('build/libs/eachend/conf')
}
```

修改配置application.yml,添加仓库配置和自动刷新配置

```yaml
server:
  port: 5679
spring:
  security:
    basic:
      enabled: true
    user:
      name: wxy
      password: wxy123
  application:
    name: config-server
  cloud:
    config:
      server:
        git:
          uri: https://github.com/pignum1/config.git
          searchPaths: '{application}'
eureka:
  client:
    service-url:
      defaultZone: http://wxy:wxy123@47.102.99.93:5678/eureka/
  instance:
    prefer-ip-address: true
    instance-id: ${spring.application.name}:${spring.application.instance_id:${server.port}}
    appname: config-server
```

在启动类上添加注解

```java
package com.example.configserver;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ConfigServerApplication.class, args);
	}
}
```

启动服务配置中心

# 创建provider生产者

创建springboot项目， 修改build.gradle文件

```groovy
compile('org.springframework.cloud:spring-cloud-starter-netflix-eureka-client')
compile('org.springframework.cloud:spring-cloud-starter-config')
compile('org.springframework.boot:spring-boot-starter-webflux')
compile('org.springframework.boot:spring-boot-starter-actuator')
compile('org.springframework.cloud:spring-cloud-starter-openfeign')
compile('org.springframework.cloud:spring-cloud-starter-netflix-hystrix')
```

创建bootstrap.properties文件

```properties
#datasource
spring.datasource.url=jdbc:mysql://localhost:3306/cloud?useSSL=false&serverTimezone=GMT%2B8
spring.datasource.username=dawei
spring.datasource.password=WEIxy.789
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

spring.jackson.date-format=yyyy-MM-dd HH:mm:ss
spring.jackson.time-zone=GMT+8

spring.jpa.properties.hibernate.hbm2ddl.auto=update
spring.jpa.database-platform=org.hibernate.dialect.MySQL5Dialect
spring.datasource.dbcp.max-wait=300

spring.application.name=provider
server.port=5682

eureka.client.service-url.defaultZone=http://wxy:wxy123@localhost:5678/eureka/

eureka.instance.status-page-url=http://${spring.cloud.client.ip-address}:${server.port}/swagger-ui.html

#心跳频率
eureka.instance.lease-renewal-interval-in-seconds=5
eureka.instance.lease-expiration-duration-in-seconds=10
```

修改启动类

```
//@EnableSwagger2
@SpringCloudApplication
//@EntityScan("com.example.provider")
//@EnableJpaRepositories("com.example.provider")
@EnableJpaAuditing
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

创建服务生产类

```
@RestController
@RequestMapping("/hello")
public class HelloController {

    @Autowired
    private UserDao userDao;

    @Autowired
    private ProviderDao providerDao;

    @ApiOperation(value = "打个招呼", notes = "打个招呼")
    @PostMapping("/hello")
    public String hello(@RequestParam String name ) {
//        Provider
        return "你好啊!"+name ;
    }
}
```



# 创建服务消费者consumer服务

新建一个spring boot服务, 修改buid.gradle

```
plugins {
	id 'org.springframework.boot' version '2.2.4.RELEASE'
	id 'io.spring.dependency-management' version '1.0.9.RELEASE'
	id 'java'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '1.8'

configurations {
	developmentOnly
	runtimeClasspath {
		extendsFrom developmentOnly
	}
	compileOnly {
		extendsFrom annotationProcessor
	}
}

repositories {
	mavenCentral()
}

ext {
	set('springCloudVersion', "Hoxton.SR1")
}

dependencies {
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
	compile('org.springframework.cloud:spring-cloud-starter-config')
	compile('org.springframework.boot:spring-boot-starter-webflux')
	compile('org.springframework.boot:spring-boot-starter-actuator')
	compile('org.springframework.cloud:spring-cloud-starter-openfeign')
	compile('org.springframework.cloud:spring-cloud-starter-netflix-hystrix')
	compileOnly 'org.projectlombok:lombok'
	developmentOnly 'org.springframework.boot:spring-boot-devtools'
	annotationProcessor 'org.projectlombok:lombok'
	testImplementation('org.springframework.boot:spring-boot-starter-test') {
		exclude group: 'org.junit.vintage', module: 'junit-vintage-engine'
	}
}

dependencyManagement {
	imports {
		mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
	}
}

test {
	useJUnitPlatform()
}
```

修改bootstrap.properties

```properties
spring.application.name=consumer


eureka.client.service-url.defaultZone=http://wxy:wxy123@localhost:5678/eureka/
eureka.instance.prefer-ip-address=true
eureka.instance.instance-id=${spring.application.name}:${spring.application.instance_id:${server.port}}
eureka.instance.appname=consumer


#服务配置中心
spring.cloud.config.discovery.service-id=config-server
spring.cloud.config.discovery.enabled=true
spring.cloud.config.fail-fast=true
spring.cloud.config.username=wxy
spring.cloud.config.password=wxy123
spring.cloud.config.profile=dev
```

启动类修改

```
@SpringBootApplication
public class ConsumerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ConsumerApplication.class, args);
	}

	@Bean
	@LoadBalanced
	public RestTemplate restTemplate(){
		RestTemplate restTemplate = new RestTemplate();
		List<HttpMessageConverter<?>> list = restTemplate.getMessageConverters();
		for (HttpMessageConverter<?> httpMessageConverter : list) {
			if(httpMessageConverter instanceof StringHttpMessageConverter) {
				((StringHttpMessageConverter) httpMessageConverter).setDefaultCharset(Charset.forName("utf-8"));
			}
		}
		return restTemplate;
	}

}
```

创建服务调用类

```java
@RestController
public class GreetHello {
    @Autowired
    private RestTemplate restTemplate;


    @PostMapping("/greet")
    @HystrixCommand(fallbackMethod = "fallbackMethod")
    public String sayHelloWorld(String parm) {
        MultiValueMap<String, String> map = new LinkedMultiValueMap<String, String>();
        map.add("name",parm);
        String res = this.restTemplate.postForObject("http://provider/hello/hello", map, String.class);
        return res;
    }

    public String fallbackMethod(){
        return "error";
    }
}
```

# fegin服务消费者

使用fegin的方式调用生产者,仍然需要新建一个spring boot项目

引入依赖,修改build.gradle

```groovy
plugins {
	id 'org.springframework.boot' version '2.2.4.RELEASE'
	id 'io.spring.dependency-management' version '1.0.9.RELEASE'
	id 'java'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '1.8'

configurations {
	developmentOnly
	runtimeClasspath {
		extendsFrom developmentOnly
	}
	compileOnly {
		extendsFrom annotationProcessor
	}
}

repositories {
	mavenCentral()
}

ext {
	set('springCloudVersion', "Hoxton.SR1")
}

dependencies {
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
	compile('org.springframework.cloud:spring-cloud-starter-config')
	compile('org.springframework.boot:spring-boot-starter-webflux')
	compile('org.springframework.boot:spring-boot-starter-actuator')
	compile('org.springframework.cloud:spring-cloud-starter-openfeign')
	compile('org.springframework.cloud:spring-cloud-starter-netflix-hystrix')

	compile('org.springframework.boot:spring-boot-starter-web')
// https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-feign
	compile group: 'org.springframework.cloud', name: 'spring-cloud-starter-feign', version: '1.4.7.RELEASE'


	compileOnly 'org.projectlombok:lombok'
	developmentOnly 'org.springframework.boot:spring-boot-devtools'
	annotationProcessor 'org.projectlombok:lombok'
	testImplementation('org.springframework.boot:spring-boot-starter-test') {
		exclude group: 'org.junit.vintage', module: 'junit-vintage-engine'
	}
}

dependencyManagement {
	imports {
		mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
	}
}

test {
	useJUnitPlatform()
}
```

修改application.properties配置，基本和ribbon的配置是一样的,

```
spring.application.name=fegin
server.port=5685

eureka.client.service-url.defaultZone=http://wxy:wxy123@47.102.99.93:5678/eureka/

eureka.instance.status-page-url=http://${spring.cloud.client.ip-address}:${server.port}/swagger-ui.html

#心跳频率
eureka.instance.lease-renewal-interval-in-seconds=5
eureka.instance.lease-expiration-duration-in-seconds=10
```

创建映射的服务调用

```java
@FeignClient(name = "provider",fallback = FeignClientFallback.class, configuration = FeignConfig.class)
public interface FeginClient {

    @PostMapping("/hello/hello")
    public String greet(@RequestParam("name") String name);
}
```

```java
@Component
public class FeignClientFallback  implements FeginClient{

    @Override
    public String greet(String name) {
        return "greet error";
    }
}
```

```java
@Configuration
public class FeignConfig {

    @Bean
    Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }
}
```

创建调用的方法

```java
@RestController
public class GreetController {

    @Autowired
     FeginClient feginClient;

    @PostMapping("/hello")
    public String  hello ( String  name ){
        return feginClient.greet(name);
    }
}
```

在启动类上添加注解

```java
@SpringCloudApplication
@EnableFeignClients
@EnableCircuitBreaker
@EnableHystrix
@ComponentScan("com.example.*")
@EnableAutoConfiguration
public class FeginApplication {

	public static void main(String[] args) {
		SpringApplication.run(FeginApplication.class, args);
	}

}
```

启动服务后就可以试着用fegin的方式调用方法打招呼的方法了

# 创建ZUUL服务网关

新建一个项目，修改build.gradle

```groovy
plugins {
	id 'org.springframework.boot' version '2.2.4.RELEASE'
	id 'io.spring.dependency-management' version '1.0.9.RELEASE'
	id 'java'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '1.8'

repositories {
	mavenCentral()
}

ext {
	set('springCloudVersion', "Hoxton.SR1")
}

dependencies {
	implementation 'org.springframework.cloud:spring-cloud-starter-netflix-zuul'

	compile('org.springframework.cloud:spring-cloud-starter-netflix-eureka-client')
	compile('org.springframework.cloud:spring-cloud-starter-config')
	compile('org.springframework.boot:spring-boot-starter-actuator')
	testImplementation('org.springframework.boot:spring-boot-starter-test') {
		exclude group: 'org.junit.vintage', module: 'junit-vintage-engine'
	}
}

dependencyManagement {
	imports {
		mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
	}
}

test {
	useJUnitPlatform()
}

```

新建bootstrap.properties，修改配置

```properties
spring.application.name=zuul


eureka.client.service-url.defaultZone=http://wxy:wxy123@localhost:5678/eureka/
eureka.instance.prefer-ip-address=true
eureka.instance.instance-id=${spring.application.name}:${spring.application.instance_id:${server.port}}
eureka.instance.appname=zuul


#服务配置中心
spring.cloud.config.discovery.service-id=config-server
spring.cloud.config.discovery.enabled=true
spring.cloud.config.fail-fast=true
spring.cloud.config.username=wxy
spring.cloud.config.password=wxy123
spring.cloud.config.profile=dev
```

git上的配置application-dev.properties内容如下,转发路劲和超时时间

```properties
server.port=5684
spring.profiles.active=dev
zuul.routes.consumer=/consumer/**
zuul.routes.provider=/provider/**
hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds=80000
```

修改启动类

```java
@EnableZuulProxy
@RefreshScope
@SpringCloudApplication
public class ZuulApplication {

	public static void main(String[] args) {
		SpringApplication.run(ZuulApplication.class, args);
	}
}
```

此时访问其他服务可以通过访问网关上的路径转发来访问其他服务，来隐藏其他服务的地址，还可以做鉴权等其他功能。