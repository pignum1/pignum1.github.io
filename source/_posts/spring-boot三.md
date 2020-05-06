---
title: spring-boot localDate等时间序列化异常
date: 2019-04-20 23:45:53
tags: [spring boot]
type: "categories"
categories: spring boot
---
# 普通时间的序列化
@nbsp;@nbsp;@nbsp;@nbsp;LocalDate、LocalTime、LocalDateTime是Java 8开始提供的时间日期API，然而我们在使用Spring Boot或使用Spring Cloud Feign的时候会出现各种问题
以前使用的Date只需要添加注解下面的注解，就能够在前后端以JSON格式传输
```
@JsonFormat(pattern = "yyyy-MM-dd")
@DateTimeFormat(pattern = "yyyy-MM-dd")
private Date date ;
```

如果使用了LocalDate等类型，在传输数据就会报错JSON parse error: Can not construct instance of java.time.LocalDate
因为默认情况下Spring MVC对于LocalDate序列化成了一个数组类型，而Feign在调用的时候，还是按照ArrayList来处理，所以自然无法反序列化为LocalDate对象了。
```
"date":[2019,1,1]
```
解决办法：
先引入jackson-datatype-jsr310依赖，再在启动类中加入
```
//      依赖中加入localDate时间转化依赖
compile group: 'com.fasterxml.jackson.datatype', name: 'jackson-datatype-jsr310', version: '2.9.8'
		
		
//		在启动类中添加
@Bean
public ObjectMapper serializingObjectMapper() {
    ObjectMapper objectMapper = new ObjectMapper();
    objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    objectMapper.registerModule(new JavaTimeModule());
    return objectMapper;
}		
```

