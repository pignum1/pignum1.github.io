---
title: spring-boot log4j记录日志
date: 2019-08-22 23:38:08
tags: [log4j ,spring boot ]
type: "categories"
categories: spring boot
---
# spring boot 集成日志
spring boot 框架本身依赖 spring-boot-starter 中包含的就有logback,如果我们引入log4j或则log4j2的时候，为了必变jar报冲突，需要排除该包的依赖
我是用的是grdle构建的项目，如下配置
```
{
	dependencies{
	//其他的省略
	compile group: 'org.springframework.boot', name: 'spring-boot-starter-log4j', version: '1.3.8.RELEASE'
	}
	
	configurations {
        all*.exclude group: 'org.springframework.boot', module: 'spring-boot-starter-logging'
    }
}
```
在resource目录下创建log4j.properties文件,按需求配置log的输出路径和级别，这里不介绍太多
```
# LOG4J配置,控制台的输出 、
# 日志输出级别 info, appender为控制台输出stdout
#log4j.rootCategory=INFO, stdout
# 控制台输出
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss,SSS} %5p %c{1}:%L - %m%n


#输出到文件里面
log4j.rootCategory=INFO, stdout, file
# root日志输出
log4j.appender.file=org.apache.log4j.DailyRollingFileAppender
#默认的路径是在根目录下 + logs/all.log ,启动时会自动创建目录和文件，在linux下还未测试
log4j.appender.file.file=logs/all.log
log4j.appender.file.DatePattern='.'yyyy-MM-dd
log4j.appender.file.layout=org.apache.log4j.PatternLayout
log4j.appender.file.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss,SSS} %5p %c{1}:%L - %m%n


# com.cloud.controller包下的日志配置
log4j.category.com.cloud.controller=DEBUG, controller
# com.cloud.controller下的日志输出
log4j.appender.controller=org.apache.log4j.DailyRollingFileAppender
log4j.appender.controller.file=logs/my.log
log4j.appender.controller.DatePattern='.'yyyy-MM-dd
log4j.appender.controller.layout=org.apache.log4j.PatternLayout
log4j.appender.controller.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss,SSS} %5p %c{1}:%L ---- %m%n
```
此时启动项目，控制台会打印出日志信息，并在设置下的日志文件路径创建日志文件，记录日志信息。

# 使用AOP记录请求到日志中
AOP是Spring框架中的一个重要内容，是对既有的一个程序定义切入点，在切入的前后执行不同的内容。在项目中引入AOP的依赖
```
 // aop切面 @Aspect
        compile group: 'org.springframework.boot', name: 'spring-boot-starter-aop', version: '2.1.6.RELEASE'
```
在完成了引入AOP依赖包后，不需要去做其他配置。不需要在程序主类中增加@EnableAspectJAutoProxy来启用，默认就是已启用。
```
实现AOP的切面主要有以下几个注解：
使用@Aspect注解将一个java类定义为切面类
使用@Pointcut定义一个切入点，可以是一个规则表达式，比如下例中某个package下的所有函数，也可以是一个注解等。
根据需要在切入点不同位置的切入内容
使用@Before在切入点开始处切入内容
使用@After在切入点结尾处切入内容
使用@AfterReturning在切入点return内容之后切入内容（可以用来对处理返回值做一些加工处理）
使用@Around在切入点前后切入内容，并自己控制何时执行切入点自身的内容
使用@AfterThrowing用来处理当切入内容部分抛出异常之后的处理逻辑
使用@Order(i)注解来标识切面的优先级。i的值越小，优先级越高
@Aspect
@Component
public class WebLogAspect {

    private Logger logger = Logger.getLogger(getClass());

   @Pointcut("execution(public * com.cloud.controller..*.*(..))")
    public void webLog(){}

       @Before("webLog()")
    public void doBefore(JoinPoint joinPoint) throws Throwable {
        // 接收到请求，记录请求内容
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();

        // 记录下请求内容
        logger.info("URL : " + request.getRequestURL().toString());
        logger.info("HTTP_METHOD : " + request.getMethod());
        logger.info("IP : " + request.getRemoteAddr());
        logger.info("CLASS_METHOD : " + joinPoint.getSignature().getDeclaringTypeName() + "." + joinPoint.getSignature().getName());
        logger.info("ARGS : " + Arrays.toString(joinPoint.getArgs()));

    }

    @AfterReturning(returning = "ret", pointcut = "webLog()")
    public void doAfterReturning(Object ret) throws Throwable {
        // 处理完请求，返回内容
        logger.info("RESPONSE : " + ret);
    }
}
```
这个时候启动服务，并调用controller下的服务，就会在日志中记录请求和返回的信息（实际中项目记录我们是保存在数据库的）
# 日志记录存放到mongodb
添加mongodb的驱动依赖
```
   // mongodb-driver，使用切面蒋日志文件写入Mongodb
        compile group: 'org.mongodb', name: 'mongodb-driver', version: '3.10.2'
```
创建写入的实现类
```
public class MongoAppender extends AppenderSkeleton {
    private MongoClient mongoClient;
    private MongoDatabase mongoDatabase;
    private MongoCollection<BasicDBObject> logsCollection;

    private  String connectionUrl ;
    private  String databaseName;
    private  String collectionName;


    @Override
    protected void append(LoggingEvent loggingEvent) {
        if(mongoDatabase == null) {
            MongoClientURI connectionString = new MongoClientURI(connectionUrl);
            mongoClient = new MongoClient(connectionString);
            mongoDatabase = mongoClient.getDatabase(databaseName);
            logsCollection = mongoDatabase.getCollection(collectionName, BasicDBObject.class);
        }
        logsCollection.insertOne((BasicDBObject) loggingEvent.getMessage());

    }

    @Override
    public void close() {
        if(mongoClient != null) {
            mongoClient.close();
        }
    }

    @Override
    public boolean requiresLayout() {
        return false;
    }
```
修改存放到mongodb的数据类型为BasicDBObject
```
@Aspect
@Order(1)
@Component
public class WebLogAspect {
    private Logger logger = Logger.getLogger("mongodb");

    @Pointcut("execution(public * com.cloud.controller..*.*(..))")
    public void webLog(){}


    @Before("webLog()")
    public void doBefore(JoinPoint joinPoint) throws Throwable {
        // 获取HttpServletRequest
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();
        // 获取要记录的日志内容
        BasicDBObject logInfo = getBasicDBObject(request, joinPoint);
        logger.info(logInfo);
    }


    private BasicDBObject getBasicDBObject(HttpServletRequest request, JoinPoint joinPoint) {
        // 基本信息
        BasicDBObject r = new BasicDBObject();
        r.append("requestURL", request.getRequestURL().toString());
        r.append("requestURI", request.getRequestURI());
        r.append("queryString", request.getQueryString());
        r.append("remoteAddr", request.getRemoteAddr());
        r.append("remoteHost", request.getRemoteHost());
        r.append("remotePort", request.getRemotePort());
        r.append("localAddr", request.getLocalAddr());
        r.append("localName", request.getLocalName());
        r.append("method", request.getMethod());
        r.append("headers", getHeadersInfo(request));
        r.append("parameters", request.getParameterMap());
        r.append("classMethod", joinPoint.getSignature().getDeclaringTypeName() + "." + joinPoint.getSignature().getName());
        r.append("args", Arrays.toString(joinPoint.getArgs()));
        return r;
    }

    private Map<String, String> getHeadersInfo(HttpServletRequest request) {
        Map<String, String> map = new HashMap<>();
        Enumeration headerNames = request.getHeaderNames();
        while (headerNames.hasMoreElements()) {
            String key = (String) headerNames.nextElement();
            String value = request.getHeader(key);
            map.put(key, value);
        }
        return map;
    }
```
在 log4j.properties配置mongodb的参数
```
# mongodb输出
log4j.logger.mongodb=INFO, mongodb
#写入的实现类全路径
log4j.appender.mongodb=com.cloud.config.MongoAppender
#路径
log4j.appender.mongodb.connectionUrl=mongodb://47.102.99.95:27017
#数据库名称
log4j.appender.mongodb.databaseName=cloud
#mongodb中集合名称
log4j.appender.mongodb.collectionName=logs_request
```





