---
title: spring-boot rabbit
date: 2019-08-25 10:38:27
tags: [rabbit ,spring boot ]
type: "categories"
categories: spring boot
---
# RabbitMQ简介
消息队列（Message Queue，简称MQ），从字面意思上看，本质是个队列，FIFO先入先出，只不过队列中存放的内容是message而已。主要用于不同进程Process/线程Thread之间通信。
消息队列的好处：
不同进程（process）之间传递消息时，两个进程之间耦合程度过高，改动一个进程，引发必须修改另一个进程，为了隔离这两个进程，在两进程间抽离出一层（一个模块），所有两进程之间传递的消息，都必须通过消息队列来传递，单独修改某一个进程，不会影响另一个。
不同进程（process）之间传递消息时，为了实现标准化，将消息的格式规范化了，并且，某一个进程接受的消息太多，一下子无法处理完，并且也有先后顺序，必须对收到的消息进行排队，因此诞生了事实上的消息队列。
MQ框架非常之多，比较流行的有RabbitMq、ActiveMq、ZeroMq、kafka，以及阿里开源的RocketMQ。
# RabbitMQ的安装
linux（centos7.6）下的安装，因为是erlang语言写的，所以首先需要安装erlang,我的习惯是创建/usr/local/erlang,/usr/local/rabbitMQ两个文件夹。
首先是安装erlang
```
//切换目录到/usr/local/erlang
cd  /usr/local/erlang
//下载
wget http://www.rabbitmq.com/releases/erlang/erlang-19.0.4-1.el7.centos.x86_64.rpm
//安装
rpm -ivh erlang-19.0.4-1.el7.centos.x86_64.rpm
//查看erlang版本
erl
```
出现下面的图样，说明安装成功了
![](/erlang.png)
接着就是安装rabbitMQ,需要注意的是erlang 和 rabbitMQ的版本关系，最好取官网上查询对应的安装版本。
```
//切换目录到rabbitMQ
cd /usr/local/rabbitMq
//下载
wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.15/rabbitmq-server-3.6.15-1.el7.noarch.rpm
//安装
rpm -ivh rabbitmq-server-3.6.15-1.el7.noarch.rpm
//检查rabbitMq是否安装成功
rpm -qa|grep rabbitmq
```
同样输入rpm -qa|grep rabbitmq会出现下面的图片
![](/rabbitmq.png)
```
//启动rabbitmq
systemctl start rabbitmq-server
//关闭rabbitmq
systemctl stop rabbitmq-server
//查看运行状态
systemctl status rabbitmq-server
//启动网页插件
rabbitmq-plugins enable rabbitmq_management
```
但是这个时候还需要开通服务器的端口，5672（服务端口）和15672（网页插件）
出现绿色running说明运行起来了
![](/rabbitmqstatus.png)
但是因为默认的rabbirmq.conf的默认配置是# loopback_users.guest = true，不能在本机外登陆guest账号，(也能改成false,就可以了)
```
//列出角色
rabbitmqctl list_users
//新增角色
rabbitmqctl add_user wxy wxy
//添加权限
rabbitmqctl set_permissions -p / wxy ".*" ".*" ".*"
//修改用户的角色(我设置的是超级管理员，还有监控者，管理者等，了解更多去官网吧)
rabbitmqctl set_user_tags wxy administrator
//删除用户
rabbitmqctl delete_user Username
//修改密码
rabbitmqctl change_password Username Newpassword
```
# rabbitmq的五种队列
创建一个虚拟的virtualhost,给用户这个分配这个虚拟服务的权限
![](/virtualhost.png)
![](/hostpermission.png)
![](/view.png)
![](/view2.png)
## 简单队列
创建一个简单的springboot服务，向消息对类中发送一段消息
```
//在build.gralde中加入依赖
//amqp-client
compile group: 'com.rabbitmq', name: 'amqp-client', version: '3.4.1'

//创建连接RabbitMQ
public class ConnectionUtil {
    public static Connection getConnection() throws Exception {
        //定义连接工厂
        ConnectionFactory factory = new ConnectionFactory();
        //设置服务地址
        factory.setHost("localhost");
        //端口
        factory.setPort(5672);
        //设置账号信息，用户名、密码、vhost
        factory.setVirtualHost("testhost");
        factory.setUsername("wxy");
        factory.setPassword("wxy");
        // 通过工程获取连接
        Connection connection = factory.newConnection();
        return connection;
    }
}

//编写测试方法发送消息到队列中
public class Send {
    private final static String QUEUE_NAME = "q_test_01";

    public static void main(String[] argv) throws Exception {
        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        // 从连接中创建通道
        Channel channel = connection.createChannel();

        // 声明（创建）队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // 消息内容
        String message = "Hello World!";
        channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
        System.out.println(" [x] Sent '" + message + "'");
        //关闭通道和连接
        channel.close();
        connection.close();
    }
}

//编辑测试方法接收消息
public class Recive {
    private final static String QUEUE_NAME = "q_test_01";

    public static void main(String[] argv) throws Exception {
        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        // 从连接中创建通道
        Channel channel = connection.createChannel();
        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        // 定义队列的消费者
        QueueingConsumer consumer = new QueueingConsumer(channel);
        // 监听队列
        channel.basicConsume(QUEUE_NAME, true, consumer);
        // 获取消息
        while (true) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            String message = new String(delivery.getBody());
            System.out.println(" [x] Received '" + message + "'");
        }
    }
}
```
运行程序后打开rabbitmq的web页面，可以发现页面上如下图所示
![](/simplesend.png)
## work模式
编辑消息发送者，队列中发送一百个消息
```
public class WorkSend {
    private final static String QUEUE_NAME = "test_queue_work";
    public static void main(String[] argv) throws Exception {
        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();

        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        for (int i = 0; i < 100; i++) {
            // 消息内容
            String message = "" + i;
            channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
            System.out.println(" [x] Sent '" + message + "'");

            Thread.sleep(i * 10);
        }
        channel.close();
        connection.close();
    }
}
```
在编辑两个消费者来接受消息
```
public class Recv1 {
    private final static String QUEUE_NAME = "test_queue_work";

    public static void main(String[] argv) throws Exception {

        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();

        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // 同一时刻服务器只会发一条消息给消费者
        channel.basicQos(0);

        // 定义队列的消费者
        QueueingConsumer consumer = new QueueingConsumer(channel);
        // 监听队列，false表示手动返回完成状态，true表示自动
        channel.basicConsume(QUEUE_NAME, true, consumer);

        // 获取消息
        while (true) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            String message = new String(delivery.getBody());
            System.out.println(" [recv1] Received '" + message + "'");
            //休眠
            Thread.sleep(10);
            // 返回确认状态，注释掉表示使用自动确认模式
            //channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }
}
```
```
public class Recv2 {
    private final static String QUEUE_NAME = "test_queue_work";

    public static void main(String[] argv) throws Exception {

        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();

        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // 同一时刻服务器只会发一条消息给消费者
        channel.basicQos(0);

        // 定义队列的消费者
        QueueingConsumer consumer = new QueueingConsumer(channel);
        // 监听队列，false表示手动返回完成状态，true表示自动
        channel.basicConsume(QUEUE_NAME, true, consumer);

        // 获取消息
        while (true) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            String message = new String(delivery.getBody());
            System.out.println(" [recv2] Received '" + message + "'");
            // 休眠1秒
            Thread.sleep(1000);
            //下面这行注释掉表示使用自动确认模式
            //channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }
}
```
测试的结果：
消费者1和消费者2获取到的消息内容是不同的，同一个消息只能被一个消费者获取。一个是消费奇数号消息，一个是偶数。
其实，这样是不合理的，因为消费者1线程停顿的时间短。应该是消费者1要比消费者2获取到的消息多才对。RabbitMQ 默认将消息顺序发送给下一个消费者，这样，每个消费者会得到相同数量的消息。即轮询（round-robin）分发消息。
怎样才能做到按照每个消费者的能力分配消息呢？联合使用 Qos 和 Acknowledge 就可以做到。
basicQos 方法设置了当前信道最大预获取（prefetch）消息数量为1。消息从队列异步推送给消费者，消费者的 ack 也是异步发送给队列，从队列的视角去看，总是会有一批消息已推送但尚未获得 ack 确认，Qos 的 prefetchCount 参数就是用来限制这批未确认消息数量的。设为1时，队列只有在收到消费者发回的上一条消息 ack 确认后，才会向该消费者发送下一条消息。prefetchCount 的默认值为0，即没有限制，队列会将所有消息尽快发给消费者。
两个概念：
轮询分发 ：使用任务队列的优点之一就是可以轻易的并行工作。如果我们积压了好多工作，我们可以通过增加工作者（消费者）来解决这一问题，使得系统的伸缩性更加容易。在默认情况下，RabbitMQ将逐个发送消息到在序列中的下一个消费者(而不考虑每个任务的时长等等，且是提前一次性分配，并非一个一个分配)。平均每个消费者获得相同数量的消息。这种方式分发消息机制称为Round-Robin（轮询）
公平分发 ：虽然上面的分配法方式也还行，但是有个问题就是：比如：现在有2个消费者，所有的奇数的消息都是繁忙的，而偶数则是轻松的。按照轮询的方式，奇数的任务交给了第一个消费者，所以一直在忙个不停。偶数的任务交给另一个消费者，则立即完成任务，然后闲得不行。而RabbitMQ则是不了解这些的。这是因为当消息进入队列，RabbitMQ就会分派消息。它不看消费者为应答的数目，只是盲目的将消息发给轮询指定的消费者。
为了解决这个问题，我们使用basicQos( prefetchCount = 1)方法，来限制RabbitMQ只发不超过1条的消息给同一个消费者。当消息处理完毕后，有了反馈，才会进行第二次发送。还有一点需要注意，使用公平分发，必须关闭自动应答，改为手动应答。
设置,只需要改动三个地方
```
// 同一时刻服务器只会发一条消息给消费者,默认是0，就算轮询的模式
channel.basicQos(1);
// 监听队列，false表示手动返回完成状态，true表示自动确认	
//只要消息从队列中获取，无论消费者获取到消息后是否成功消息，都认为是消息已经成功消费。
channel.basicConsume(QUEUE_NAME, false, consumer);
//开启手动确认
channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
```
## 订阅模式
创建消息生产这，并把消息把固定到交换机上,直接放代码吧
```
public class Send {
    private final static String EXCHANGE_NAME = "test_exchange_fanout";

    public static void main(String[] argv) throws Exception {
        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();

        // 声明exchange
        channel.exchangeDeclare(EXCHANGE_NAME, "fanout");

        // 消息内容
        String message = "Hello World!";
        channel.basicPublish(EXCHANGE_NAME, "", null, message.getBytes());
        System.out.println(" [x] Sent '" + message + "'");

        channel.close();
        connection.close();
    }
}
```
这个时候再创建两个消息队列，且都绑定在交换机上,如下
```
public class Recv1 {
    private final static String QUEUE_NAME = "test_queue_work1"; //另一个Recv2写成test_queue_work2
    private final static String EXCHANGE_NAME = "test_exchange_fanout";
    public static void main(String[] argv) throws Exception {
        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();
        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        // 绑定队列到交换机
        channel.queueBind(QUEUE_NAME, EXCHANGE_NAME, "");
        // 同一时刻服务器只会发一条消息给消费者
        channel.basicQos(1);
        // 定义队列的消费者
        QueueingConsumer consumer = new QueueingConsumer(channel);
        // 监听队列，手动返回完成
        channel.basicConsume(QUEUE_NAME, false, consumer);
        // 获取消息
        while (true) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            String message = new String(delivery.getBody());
            System.out.println(" [Recv1] Received '" + message + "'");
            Thread.sleep(10);
            channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }
}
```
这个时候启动sender和Recv1、Recv2,就能看见两个消息队列的监听同时打印出 "hello world!"
## 主题模式（匹配符模式）
匹配符模式与订阅模式基本相同，只是再发送消息和接收消息添加了routeKey得规则
```
public class Sender {
    public static final String EXCHANGE_NAME = "test_exchange_topic";

    public static void main(String[] args) throws Exception {
        Connection connection = ConnectionUtil.getConnection();
        //获取连接通道
        Channel channel = connection.createChannel();
        //生命交换机名称  和  类型
        channel.exchangeDeclare( EXCHANGE_NAME,"topic" );

        String message = "hello rabbitmq topic theme";
        channel.basicPublish( EXCHANGE_NAME,"routeKey.1",null,message.getBytes());
        System.out.println(" topic sender send :["+message+"]");
        //关闭通道和连接
        channel.close();
        connection.close();
    }
}

public class Recv1 {
    private final static String QUEUE_NAME = "test_queue_topic_work_1";

    private final static String EXCHANGE_NAME = "test_exchange_topic";

    public static void main(String[] argv) throws Exception {

        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();

        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // 绑定队列到交换机
        channel.queueBind(QUEUE_NAME, EXCHANGE_NAME, "routeKey.*");

        // 同一时刻服务器只会发一条消息给消费者
        channel.basicQos(1);

        // 定义队列的消费者
        QueueingConsumer consumer = new QueueingConsumer(channel);
        // 监听队列，手动返回完成
        channel.basicConsume(QUEUE_NAME, false, consumer);

        // 获取消息
        while (true) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            String message = new String(delivery.getBody());
            System.out.println(" [topic Receiver 1] Received '" + message + "'");
            Thread.sleep(10);

            channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }
}

public class Recv2 {
    private final static String QUEUE_NAME = "test_queue_topic_work_2";

    private final static String EXCHANGE_NAME = "test_exchange_topic";

    public static void main(String[] argv) throws Exception {

        // 获取到连接以及mq通道
        Connection connection = ConnectionUtil.getConnection();
        Channel channel = connection.createChannel();

        // 声明队列
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // 绑定队列到交换机
        channel.queueBind(QUEUE_NAME, EXCHANGE_NAME, "*.*");

        // 同一时刻服务器只会发一条消息给消费者
        channel.basicQos(1);

        // 定义队列的消费者
        QueueingConsumer consumer = new QueueingConsumer(channel);
        // 监听队列，手动返回完成
        channel.basicConsume(QUEUE_NAME, false, consumer);

        // 获取消息
        while (true) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            String message = new String(delivery.getBody());
            System.out.println(" [topic Receiver 2] Received '" + message + "'");
            Thread.sleep(10);

            channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        }
    }

}
```
这里的channel.queueBind(QUEUE_NAME, EXCHANGE_NAME, "routeKey.*");表示得过滤规则，满足 routeKey.*得key得队列才会接收到，#表示得是一个或多个字符，而*表示得是一个字符

# spring boot 使用rabbitmq
新建一个spring boot项目，引入依赖包和配置端口和上面一样
创建redis的配置文件，这里直接贴上代码
```
@Configuration
public class TopicRabbitConfig {

    /**
     * 简单模式下的消息队列配置，默认是按劳分配得队列获取
     *
     * @return
     */
    @Bean
    public Queue helloQueue() {
        return new Queue( "hello" );
    }

//---------------------分割线   主题模式--------------------------------//

    /**
     * 定义两个消息队列
     */
    private final static String message = "q_topic_message";
    private final static String messages = "q_topic_messages";
    private final static String exchange = "topic_exchange";

    @Bean
    public Queue queueMessage() {
        return new Queue( TopicRabbitConfig.message );
    }

    @Bean
    public Queue queueMessages() {
        return new Queue( TopicRabbitConfig.messages );
    }

    /**
     * 声明一个Topic类型的交换机
     *
     * @return
     */
    @Bean
    TopicExchange exchange() {
        return new TopicExchange( exchange );
    }

    /**
     * queueMessage绑定到交换机上，并设置匹配得规则
     */
    @Bean
    Binding bindingExchangeMessage(Queue queueMessage,TopicExchange exchange) {
        return BindingBuilder.bind( queueMessage ).to( exchange ).with( "topic.message" );
    }

    /**
     * queueMessage绑定到交换机上，并设置匹配得规则
     * - 是匹配一个或多个词   *只匹配一个
     */
    @Bean
    Binding bindingExchangeMessages(Queue queueMessages,TopicExchange exchange) {
        return BindingBuilder.bind( queueMessages ).to( exchange ).with( "topic.-" );
    }

    //------------------------分割线     订阅模式----------------------------------//

    //订阅模式下得配置与主题模式基本相同，区别是不添加匹配规则
    @Bean
    public Queue aMessage() {
        return new Queue( "q_fanout_A" );
    }

    @Bean
    public Queue bMessage() {
        return new Queue( "q_fanout_B" );
    }

    @Bean
    public Queue cMessage() {
        return new Queue( "q_fanout_C" );
    }

    /**
     * 定义交换机
     * @return
     */
    @Bean
    FanoutExchange fanoutExchange() {
        return new FanoutExchange( "fanout_exchange" );
    }

    /**
     * 将交换机和队列绑定
     */
    @Bean
    Binding bindingExchangeA(Queue aMessage,FanoutExchange fanoutExchange) {
        return BindingBuilder.bind( aMessage ).to( fanoutExchange );
    }

    @Bean
    Binding bindingExchangeB(Queue bMessage,FanoutExchange fanoutExchange) {
        return BindingBuilder.bind( bMessage ).to( fanoutExchange );
    }

    @Bean
    Binding bindingExchangeC(Queue cMessage,FanoutExchange fanoutExchange) {
        return BindingBuilder.bind( cMessage ).to( fanoutExchange );
    }

}
```
下面创建不同的类型的消息发送和消息接收者
消费者默认按劳分配，不是平均分配,主要的模式配置其实都在配置类中完成。
```
@Component
public class Sender {
    @Autowired
    private AmqpTemplate rabbitTemplate;

    public void send() {
        String context = "hello " + new Date();
        System.out.println("Sender : " + context);
        // 设置  routeKey,简单模式下，这个就是队列名
        this.rabbitTemplate.convertAndSend("hello", context);
    }
}
@Component
@RabbitListener(queues = "hello")
public class Receiver1 {
    @RabbitHandler
    public void process(String hello) {
        System.out.println("Receiver : " + hello);
    }
}
```










