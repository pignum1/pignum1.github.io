---
title: spring-boot创建webService
date: 2019-11-20 11:16:14
tags: [webService,spring boot]
type: "categories"
categories: spring boot
---

# Spring boot 创建webService接口

## 环境

- **JDK 1.80_121** 
- **spring boot :2.2.1.RELEASE**
-  **cxf-spring-boot-starter-jaxws：3.2.5** 

##  创建springboot 项目

添加gradle依赖

```groovy
	// https://mvnrepository.com/artifact/org.apache.cxf/cxf-spring-boot-starter-jaxws
	compile group: 'org.apache.cxf', name: 'cxf-spring-boot-starter-jaxws', version: '3.2.5'
// https://mvnrepository.com/artifact/org.apache.commons/commons-lang3
	compile group: 'org.apache.commons', name: 'commons-lang3', version: '3.4'
```

webService注解图示

![](webservice.png)



## 创建webService接口

### 创建接口

```java
@WebService
public interface WSDemoService {
    @WebMethod
    String hello(@WebParam(name = "friend") String friend);
}
```

###  创建实现类

``` java
@Component
@Service
@WebService(name = "demoservice", targetNamespace = "http://WSDemoService.controller.webdemo1.example.com/" ,endpointInterface = "com.example.webdemo1.controller.WSDemoService")
public class WSDemoServiceImpl implements WSDemoService {
    @Override
    public String hello(String friend) {
        if (StringUtils.isBlank(friend)) {
            return "Who are you ?";
        }
        return "Hello " + friend + "!";
    }
}
```

### 注册及发布服务

这个地方的

```java

import org.apache.cxf.Bus;
import org.apache.cxf.bus.spring.SpringBus;
import org.apache.cxf.jaxws.EndpointImpl;
import org.apache.cxf.transport.servlet.CXFServlet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.xml.ws.Endpoint;

/**
 * @author WXY
 * @ClassName WebServiceConfig
 * @Description T0D0
 * @Date 2019/11/20 1:02
 * @Version 1.0
 **/
@Configuration
public class WebServiceConfig {
    @Bean(name = "cxfServlet")
    public ServletRegistrationBean dispatcherServlet() {
        return new ServletRegistrationBean(new CXFServlet(), "/service/*");
    }

    @Bean(name = Bus.DEFAULT_BUS_ID)
    public SpringBus springBus() {
        return new SpringBus();
    }


    @Autowired
    private WSDemoService demoService; //由于在实现类中加了@Service因此此处无需初始化实例

    /* 注册服务示例*/
    @Bean
    public Endpoint endpoint() {
        EndpointImpl endpoint = new EndpointImpl(springBus(), demoService);
        endpoint.publish("/test");
        return endpoint;
    }
}
```

### 访问接口

启动服务，并本地访问 * http://localhost:8080/service *可以查看所有发布的webService接口

![](serviceShow.png)



# xml格式数据的webService接口

​		虽然现在大部分结构数据格式是json,但是和一些老系统对接还是会用到webService这种跨语言的的接口，传输的数据格式也是XML。

## 在项目中添加依赖

xml转换使用的工具是XmlMapper工具，

```groovy
//	xml
	compile group: 'com.fasterxml.jackson.core', name: 'jackson-core', version: '2.10.0'
	compile group: 'com.fasterxml.jackson.core', name: 'jackson-databind', version: '2.10.0'
	compile group: 'com.fasterxml.jackson.dataformat', name: 'jackson-dataformat-xml', version: '2.10.0'
```

## XML注解

```java
@JacksonXmlRootElement用于类名，是xml最外层的根节点。注解中有localName属性，该属性如果不设置，那么生成的XML最外面就是Clazz.
@JacksonXmlCData注解是为了生成<![CDATA[text]]>
@JacksonXmlProperty注解通常可以不需要，若不用，生成xml标签名称就是实体类属性名称。但是如果你想要你的xml节点名字，首字母大写。比如例子中的Content，那么必须加这个注解，并且注解的localName填上你想要的节点名字。最重要的是！实体类原来的属性content必须首字母小写！否则会被识别成两个不同的属性。注解的isAttribute，确认是否为节点的属性，如上面“gradeId”。
@JacksonXmlElementWrapper一般用于list，list外层的标签。若不用的话，useWrapping =false
@JacksonXmlText，用实体类属性上，说明该属性是否为简单内容，如果是，那么生成xml时，不会生成对应标签名称
@JsonIgnore，忽略该实体类的属性，该注解是用于实体类转json的，但用于转xml一样有效，具体原因个人推测是XmlMapper是ObjectMapper的子类。
```



 ## 创建XML数据实体

```java
public class GradeDomain  {

    @JacksonXmlProperty(localName = "gradeId",isAttribute = true)
    private int gradeId;

    @JacksonXmlText
    private String gradeName;


    public int getGradeId() {
        return gradeId;
    }

    public void setGradeId(int gradeId) {
        this.gradeId = gradeId;
    }

    public String getGradeName() {
        return gradeName;
    }

    public void setGradeName(String gradeName) {
        this.gradeName = gradeName;
    }
}
```

```java
public class ScoreDomain {

    @JacksonXmlProperty(localName = "scoreName")
    @JacksonXmlCData
    private String name;

    @JacksonXmlProperty(localName = "scoreNumber")
    private int score;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getScore() {
        return score;
    }

    public void setScore(int score) {
        this.score = score;
    }
}
```

```java
@JacksonXmlRootElement(localName = "student")
public class StudentDomain {

    @JsonIgnore
    private String studentName;

    @JacksonXmlProperty(localName = "age")
    @JacksonXmlCData
    private int age;

    @JacksonXmlProperty(localName = "grade")
    private GradeDomain grade;

    @JacksonXmlElementWrapper(localName = "scoreList")
    @JacksonXmlProperty(localName = "score")
    private List<ScoreDomain> scores;

}
```

## 创建服务接口

```java
 @WebMethod
    public OperateResult dataCheck(@WebParam(name = "student")StudentDomain studentDomain);
```

## XmlMapper配置属性

```java
ObjectMapper xmlMapper = new XmlMapper();
//反序列化时，若实体类没有对应的属性，是否抛出JsonMappingException异常，false忽略掉
xmlMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
//序列化是否绕根元素，true，则以类名为根元素
xmlMapper.configure(SerializationFeature.WRAP_ROOT_VALUE, false);
//忽略空属性
xmlMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
//XML标签名:使用骆驼命名的属性名，
xmlMapper.setPropertyNamingStrategy(PropertyNamingStrategy.UPPER_CAMEL_CASE);
//设置转换模式
xmlMapper.enable(MapperFeature.USE_STD_BEAN_NAMING);
```



```
 @Override
    public OperateResult dataCheck(StudentDomain studentDomain) {
        try {

            ObjectMapper xmlMapper = new XmlMapper();
            xmlMapper.configure( DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES,false );
            xmlMapper.configure( SerializationFeature.WRAP_ROOT_VALUE,false );
            xmlMapper.setSerializationInclusion( JsonInclude.Include.NON_NULL );
            xmlMapper.setPropertyNamingStrategy( PropertyNamingStrategy.UPPER_CAMEL_CASE );
            xmlMapper.enable( MapperFeature.USE_STD_BEAN_NAMING );



            StudentDomain domain = new StudentDomain();
            domain.setStudentName( "张三" );
            domain.setAge( 18 );
            GradeDomain grade = new GradeDomain();
            grade.setGradeId( 1 );
            grade.setGradeName( "高三" );
            domain.setGrade( grade );
            ScoreDomain score1 = new ScoreDomain();
            score1.setName( "语文" );
            score1.setScore( 90 );
            ScoreDomain score2 = new ScoreDomain();
            score2.setName( "数学" );
            score2.setScore( 98 );
            ScoreDomain score3 = new ScoreDomain();
            score3.setName( "英语" );
            score3.setScore( 91 );
            List<ScoreDomain> scores = Arrays.asList( score1,score2,score3 );
            domain.setScores( scores );
            String xml = xmlMapper.writeValueAsString( domain );
            System.out.println( xml );
            StudentDomain studentDomain1 = xmlMapper.readValue( xml,StudentDomain.class );
            System.out.println( studentDomain1 );


            return new OperateResult( "S","嘿嘿嘿" );
        }catch (Exception e){
            e.printStackTrace();
            return new OperateResult("F","哈哈哈");
        }
    }
```

再启动服务调用 http://localhost:8080/service/test?wsdl ，可以使用soapui测试接口

# 生成客户端

 右键生成的目标包 -> 菜单拉倒最后一个 “WebServices",输入WSDL生成客户端，![](client.png)

创建测试代码

```java
 public static void main(String[] args) {
        WSDemoServiceImplService service = new WSDemoServiceImplService(
                WSDemoServiceImplService.WSDEMOSERVICEIMPLSERVICE_WSDL_LOCATION,
                WSDemoServiceImplService.WSDEMOSERVICEIMPLSERVICE_QNAME);

        System.out.println("下面是hello打印的数据");
        System.out.println(service.getDemoservicePort().hello("haha"));
        System.out.println("下面是dataCheck打印的数据");
        OperateResult operateResult = service.getDemoservicePort().dataCheck( null );
        System.out.println(service.getDemoservicePort().dataCheck( null ));
    }
```

关于webService整理就到这了.. 

 