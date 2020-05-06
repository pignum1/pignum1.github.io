---
title: spring-boot 发送邮件
date: 2019-04-20 23:45:53
tags: [spring boot]
type: "categories"
categories: spring boot
---
# 使用springboot 发送邮件功能
项目结构
![](/construct.png)
 首先在build.gradle中加入邮件依赖
```
 compile group: 'org.springframework.boot', name: 'spring-boot-starter-mail', version: '2.1.3.RELEASE'
```
 然后在application.properties中添加邮箱的信息，我用的是QQ邮箱，在使用QQ邮箱时要先设置，
 进入邮箱-> 设置 ->账户->POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务-> 开启POP3/SMTP服务
![](/邮箱验证密码.png)
 ```
spring.mail.host=smtp.qq.com
#邮箱账户
spring.mail.username=用户名
#这里的密码就是开通SMTP服务后上图的密码
spring.mail.password=密码
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true
spring.mail.properties.mail.smtp.starttls.required=true
 ```
 会根据配置文件中的内容去创建JavaMailSender实例，因此我们可以直接在需要使用的地方直接@Autowired来引入邮件发送对象。
 ## 简单文本邮件发送
 ```
@RestController
public class MailSendController {
    /**
     * 根据配置文件创建发送邮件的实例
     */
    @Autowired
    private JavaMailSender javaMailSender;

    @Autowired
    private VelocityEngine velocityEngine;

    /**
     * 简单文字邮件发送
     * @return
     */
    @PostMapping("/sendEmail")
    public OperateResult sendEmail(){
        try {
            //邮件内容
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom( "from");
            message.setTo( "to" );
            message.setSubject( "主题：简单邮件" );
            message.setText( "测试邮件内容" );
            javaMailSender.send( message );
            return OperateResult.operationSuccess( "发送邮件成功" );
        }catch (Exception e){
            e.printStackTrace();
            return OperateResult.operationFailure( e.getMessage() );
        }
    }
}
 ```
 ## 包含附件的邮件发送
 实际过程中，我们很可能会发送附件给对方
 ```
  /**
     * 发送带附件的邮件
     */
    @PostMapping("/sendEmailFile")
    public OperateResult sendEmailFile(){
        try {
            //邮件内容
            MimeMessage mimeMessage = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, true);
            helper.setFrom( "from" );
            helper.setTo( "to" );
            helper.setSubject( "主题：附件邮件" );
            helper.setText( "附件邮件内容" );
			//附件我放在了resources下
            FileSystemResource file = new FileSystemResource(new File(Thread.currentThread().getContextClassLoader().getResource("test.jpg").getFile()));
            helper.addAttachment("附件-1.jpg", file);
            helper.addAttachment("附件-2.jpg", file);


            javaMailSender.send( mimeMessage );
            return OperateResult.operationSuccess( "发送邮件成功" );
        }catch (Exception e){
            e.printStackTrace();
            return OperateResult.operationFailure( e.getMessage() );
        }
    }
 ```

 ## 潜入静态资源的邮件
 ```
   @PostMapping("/sendEmailQuiet")
    public OperateResult sendEmailQuiet(){
        try {
            //邮件内容
            MimeMessage mimeMessage = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, true);
            helper.setFrom( "from" );
            helper.setTo( "to" );
            helper.setSubject( "主题：嵌入静态资源邮件" );
            helper.setText( "嵌入静态资源邮件邮件内容" );
            helper.setText("<html><body><img src=\"cid:test\" ></body></html>", true);

            FileSystemResource file = new FileSystemResource(new File(Thread.currentThread().getContextClassLoader().getResource("test.jpg").getFile()));
            helper.addInline("test", file);
            javaMailSender.send( mimeMessage );
            return OperateResult.operationSuccess( "发送邮件成功" );
        }catch (Exception e){
            e.printStackTrace();
            return OperateResult.operationFailure( e.getMessage() );
        }
    }
 ```
 ## 发送模板邮件
 项目中引入模板的依赖
 ```
 //        邮件嵌入静态资源
        compile group: 'org.springframework.boot', name: 'spring-boot-starter-velocity', version: '1.4.7.RELEASE'
 ```
 在路径resources/templates/下，创建一个模板页面template.vm，内容如下
 ```
 <html>
<body>
    <h3>你好， ${username}, 这是一封模板邮件!</h3>
</body>
</html>
 ```
 发送模板的邮件
 ```
 @PostMapping("/sendEmailQuiet")
    public OperateResult sendEmailQuiet(){
        try {
            //邮件内容
            MimeMessage mimeMessage = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, true);
            helper.setFrom( "from" );
            helper.setTo( "to" );
            helper.setSubject( "主题：嵌入静态资源邮件" );
            helper.setText( "嵌入静态资源邮件邮件内容" );
            helper.setText("<html><body><img src=\"cid:test\" ></body></html>", true);

            FileSystemResource file = new FileSystemResource(new File(Thread.currentThread().getContextClassLoader().getResource("test.jpg").getFile()));
            helper.addInline("test", file);
            javaMailSender.send( mimeMessage );
            return OperateResult.operationSuccess( "发送邮件成功" );
        }catch (Exception e){
            e.printStackTrace();
            return OperateResult.operationFailure( e.getMessage() );
        }
    }
 ``
 

 
 


 ```