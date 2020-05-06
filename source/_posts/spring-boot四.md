---
title: spring-boot xml格式消息转换
date: 2019-08-05 23:45:53
tags: [spring boot]
type: "categories"
categories: spring boot
---
# 消息转换器（Message Converter）
在spring boot中出路HTTP请求的实现使用的是spring MVC 。而在Spring MVC中有一个消息转换器这个概念，它主要负责处理各种不同格式的请求数据进行处理，并包转换成对象，以提供更好的编程体验。
在Spring MVC中定义了HttpMessageConverter接口，抽象了消息转换器对类型的判断、对读写的判断与操作，具体可见如下定义：
```
public interface HttpMessageConverter<T> {
    boolean canRead(Class<?> clazz, @Nullable MediaType mediaType);
    boolean canWrite(Class<?> clazz, @Nullable MediaType mediaType);
    List<MediaType> getSupportedMediaTypes();
    T read(Class<? extends T> clazz, HttpInputMessage inputMessage) throws IOException, HttpMessageNotReadableException;
    void write(T t, @Nullable MediaType contentType, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException;
}
```
HTTP请求的Content-Type有各种不同格式定义，如果要支持Xml格式的消息转换，就必须要使用对应的转换器。Spring MVC中默认已经有一套采用Jackson实现的转换器MappingJackson2XmlHttpMessageConverter。
常用的HTTP请求中header传输MediaType 类型，常用的是application/json，application/xml.前后端传输数据常用格式是json,但也有接口之间采用的是XML的方式传输数据
传统的Spring应用中，我们可以通过如下配置加入对Xml格式数据的消息转换实现：
```
@Configuration
public class MessageConverterConfig1 extends WebMvcConfigurerAdapter {
    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        Jackson2ObjectMapperBuilder builder = Jackson2ObjectMapperBuilder.xml();
        builder.indentOutput(true);
        converters.add(new MappingJackson2XmlHttpMessageConverter(builder.build()));
    }
}
```
而在springboot应用中，只需要加入jackson-dataformat-xml依赖，Spring Boot就会自动引入MappingJackson2XmlHttpMessageConverter的实现：
```
compile group: 'com.fasterxml.jackson.dataformat', name: 'jackson-dataformat-xml', version: '2.9.8'
```
## 建立实体和XML的转换关系
```
@JacksonXmlRootElement(localName = "XmlPojo")
public class XmlPojo {
    @JacksonXmlProperty(localName = "message1")
    private String message1;
    @JacksonXmlProperty(localName = "message2")
    private Integer message2;
	//get、set方式省略
```
这个实体转成XML的对应关系为
```
<XmlPojo>
    <message1>*</message1>
    <message2>*</message2>
</XmlPojo>
```
## 请求于接收XML格式的数据
XML格式的消息发送,我使用的是postman工具发起的请求，在header中指定数据类型 Content-Type: application/xml，发送的数据为
```
<XmlPojo>
    <message1>message1</message1>
    <message2>2</message2>
</XmlPojo>
```
接收参数并返回XML。consumes = MediaType.APPLICATION_XML_VALUE,produces = MediaType.APPLICATION_XML_VALUE
```
    @ResponseBody
    @PostMapping(value = "/xmlTest2",consumes = MediaType.APPLICATION_XML_VALUE,
            produces = MediaType.APPLICATION_XML_VALUE)
    public XmlPojo xmlTest2(@RequestBody XmlPojo xml){
        return xml;
    }
```


