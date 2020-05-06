---
title: spring-boot web模板引擎和统一异常处理
date: 2019-04-20 23:45:53
tags: [spring boot]
type: "categories"
categories: spring boot
---
#  spring boot 模板引擎
&nbsp;&nbsp;&nbsp;&nbsp;在我们开发Web应用的时候，需要引用大量的js、css、图片等静态资源。在动态HTML实现上Spring Boot依然可以完美胜任，并且提供了多种模板引擎的默认配置支持，所以在推荐的模板引擎下，我们可以很快的上手开发动态网站。
Spring Boot提供了默认配置的模板引擎主要有以下几种：
&nbsp;&nbsp;&nbsp;&nbsp;ymeleaf
&nbsp;&nbsp;&nbsp;&nbsp;FreeMarker
&nbsp;&nbsp;&nbsp;&nbsp;Velocity
&nbsp;&nbsp;&nbsp;&nbsp;Groovy
&nbsp;&nbsp;&nbsp;&nbsp;Mustache
当你使用上述模板引擎中的任何一个，它们默认的模板配置路径为：src/main/resources/templates。当然也可以修改这个路径，具体如何修改，可在后续各模板引擎的配置属性中查询并修改。

## 使用Thymeleaf的示例
&nbsp;&nbsp;&nbsp;&nbsp;Thymeleaf是一个XML/XHTML/HTML5模板引擎，可用于Web与非Web环境中的应用开发。它是一个开源的Java库，基于Apache License 2.0许可，由Daniel Fernández创建，该作者还是Java加密库Jasypt的作者。
&nbsp;&nbsp;&nbsp;&nbsp;Thymeleaf提供了一个用于整合Spring MVC的可选模块，在应用开发中，你可以使用Thymeleaf来完全代替JSP或其他模板引擎，如Velocity、FreeMarker等。Thymeleaf的主要目标在于提供一种可被浏览器正确显示的、格式良好的模板创建方式，因此也可以用作静态建模。你可以使用它创建经过验证的XML与HTML模板。相对于编写逻辑或代码，开发者只需将标签属性添加到模板中即可。接下来，这些标签属性就会在DOM（文档对象模型）上执行预先制定好的逻辑。
&nbsp;&nbsp;&nbsp;&nbsp;在Spring Boot中使用Thymeleaf，只需要引入下面依赖，并在默认的模板路径src/main/resources/templates下编写模板文件
```
       compile group: 'org.springframework.boot', name: 'spring-boot-starter-thymeleaf', version: '2.0.6.RELEASE'
```
在完成配置之后，举一个简单的例子，在快速入门工程的基础上，举一个简单的示例来通过Thymeleaf渲染一个页面。使用的是@Controller而不是@RestController 因为@RestController是@ReponseBody和@Controller，发布会的结果默认是JSON格式
```
@Controller
public class HelloController {
    @RequestMapping("/")
    public String index(ModelMap map) {
        // 加入一个属性，用来在模板中读取
        map.addAttribute("host", "  应该替换成的文字");
        // return模板文件的名称，对应src/main/resources/templates/index.html
        return "index";  
    }

}
```
在templates下创建一个 index.html文件
```
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8" />
    <title></title>
</head>
<body>
<h1 th:text="${host}">为被替换的文字</h1>
</body>
</html>
```
springboot的默认配置
```
#thymeleaf的默认配置
# Enable template caching.
spring.thymeleaf.cache=true
# Check that the templates location exists.
spring.thymeleaf.check-template-location=true
# Content-Type value.
spring.thymeleaf.content-type=text/html
# Enable MVC Thymeleaf view resolution.
spring.thymeleaf.enabled=true
# Template encoding.
spring.thymeleaf.encoding=UTF-8 
# Comma-separated list of view names that should be excluded from resolution.
spring.thymeleaf.excluded-view-names=
# Template mode to be applied to templates. See also StandardTemplateModeHandlers.
spring.thymeleaf.mode=HTML5
# Prefix that gets prepended to view names when building a URL.
spring.thymeleaf.prefix=classpath:/templates/
# Suffix that gets appended to view names when building a URL.
spring.thymeleaf.suffix=.html
#spring.thymeleaf.template-resolver-order= # Order of the template resolver in the chain. spring.thymeleaf.view-names= # Comma-separated list of view names that can be resolved.

```
这个时候运行成功后访问localhost:port  就可以看见页面上的内容
# 自定义异常
自定义异常
```
public class MyException extends Exception {
    public MyException(String message) {
        super(message);
    }
}
```
创建全局异常处理类：通过使用@ControllerAdvice定义统一的异常处理类，而不是在每个Controller中逐个定义。@ExceptionHandler用来定义函数针对的异常类型，最后将Exception对象和请求URL映射到error.html中
船舰异常的处理类，@ExceptionHandler是标识这个方法是处理什么类型的异常
```
@ControllerAdvice
class GlobalExceptionHandler {

    public static final String DEFAULT_ERROR_VIEW = "error";

    @ExceptionHandler(value = NullPointerException.class)
    public ModelAndView defaultErrorHandler(HttpServletRequest req, Exception e) throws Exception {
        ModelAndView mav = new ModelAndView();
        mav.addObject("exception", e);
        mav.addObject("url", req.getRequestURL());
        mav.setViewName(DEFAULT_ERROR_VIEW);
        return mav;
    }
}
```
实现error.html页面展示：在templates目录下创建error.html，将请求的URL和Exception对象的message输出。
```
<!DOCTYPE html>
<html xmlns:th="http://www.w3.org/1999/xhtml">
<head lang="en" xmlns:th="http://www.thymeleaf.org">
    <meta charset="UTF-8" />
    <title>统一异常处理</title>
</head>
<body>
<h1>Error Handler</h1>

<h3>url: ${url}</h3>
<h3>message:${exception}</h3>
</body>
</html>
```
创建一个抛出异常的请求
```
	@RequestMapping("/json")
    public String  json() throws MyException {
        throw new MyException("发生错误2");
    }
```
这个时候请求/json方法，就会返回error界面，并显示出错误的请求路径和错误信息
如果需要返回的是JSON类型的格式，只需要返回的加上@ReponseBody注解
```
异常信息类
public class ErrorInfo<T> {
    public static final Integer OK = 0;
    public static final Integer ERROR = 100;
    private Integer code;
    private String message;
    private String url;
    private T data;
    // 省略getter和setter
}
```
在异常处理方法中改写为
```
    @ExceptionHandler(value = MyException.class)
    @ResponseBody  //这个注解是返回JSON格式
    public ErrorInfo<String> defaultErrorHandler(HttpServletRequest req,MyException e) throws Exception {
        ErrorInfo<String> r = new ErrorInfo<>();
        r.setMessage(e.getMessage());
        r.setCode(ErrorInfo.ERROR);
        r.setData("Some Data");
        r.setUrl(req.getRequestURL().toString());
        return r;
    }
```

