---
title: spring-boot redis
date: 2019-08-10 20:23:05
tags: [redis ,redis ]
type: "categories"
categories: spring boot
---
# redis 
&nbsp;&nbsp;&nbsp;&nbsp;Springboot整合Redis有两种方式，分别是Jedis和RedisTemplate,Jedis是Redis官方推荐的面向Java的操作Redis的客户端，而RedisTemplate是SpringDataRedis中对JedisApi的高度封装。其实在Springboot的官网上我们也能看到，官方现在推荐的是SpringDataRedis形式，相对于Jedis来说可以方便地更换Redis的Java客户端，其比Jedis多了自动管理连接池的特性，方便与其他Spring框架进行搭配使用如：SpringCache。
我的spring boot 版本是1.4.5，所以和spring boot 2.x可能会有些不一样
# spring boot 1.x 引入redis连接
首先引入redis的依赖
```
		//redis
        compile group: 'org.springframework.data', name: 'spring-data-redis', version: '1.7.2.RELEASE'
        // jedis
        compile group: 'redis.clients', name: 'jedis', version: '2.9.0'
```
在application。properties中配置redis的设置和链接地址
```
# REDIS (RedisProperties)
# Redis数据库索引（默认为0）
spring.redis.database=0
# Redis服务器地址
spring.redis.host=xx.xxx.xx.xx
# Redis服务器连接端口
spring.redis.port=6379
#客户端超时时间单位是毫秒 默认是2000
spring.redis.timeout=10000
#最大空闲数
spring.redis.maxIdle=300
#连接池的最大数据库连接数。设为0表示无限制,如果是jedis 2.4以后用redis.maxTotal
#redis.maxActive=600
#控制一个pool可分配多少个jedis实例,用来替换上面的redis.maxActive,如果是jedis 2.4以后用该属性
spring.redis.maxTotal=1000
#最大建立连接等待时间。如果超过此时间将接到异常。设为-1表示无限制。
spring.redis.maxWaitMillis=1000
#连接的最小空闲时间 默认1800000毫秒(30分钟)
spring.redis.minEvictableIdleTimeMillis=300000
#每次释放连接的最大数目,默认3
spring.redis.numTestsPerEvictionRun=1024
#逐出扫描的时间间隔(毫秒) 如果为负数,则不运行逐出线程, 默认-1
spring.redis.timeBetweenEvictionRunsMillis=30000
#是否在从池中取出连接前进行检验,如果检验失败,则从池中去除连接并尝试取出另一个
spring.redis.testOnBorrow=true
#在空闲时检查有效性, 默认false
```
在spring b00t 1.0中，编写简单的测试用例
```
@Autowired
	private StringRedisTemplate stringRedisTemplate;

	@Test
	public void test() throws Exception {
		// 保存字符串
		stringRedisTemplate.opsForValue().set("aaa", "111");
		Assert.assertEquas("111", stringRedisTemplate.opsForValue().get("aaa"));
    }
```
用redisDesktopManager打开redis就会看见redis中存入了一个key-value的数据
![](/aaa.png)
通过上面这段极为简单的测试案例演示了如何通过自动配置的StringRedisTemplate对象进行Redis的读写操作，该对象从命名中就可注意到支持的是String类型。如果有使用过spring-data-redis的开发者一定熟悉RedisTemplate<K, V>接口，StringRedisTemplate就相当于RedisTemplate<String, String>的实现。
## redis存放对象RedisTemplate
除了String类型，实经常会在Redis中存储对象，这时候我们就会想是否可以使用类似RedisTemplate<String, User>来初始化并进行操作。但是Spring Boot并不支持直接使用，需要我们自己实现RedisSerializer<T>接口来对传入对象进行序列化和反序列化
所以序列化和反序列化的方法需要我们重写,首先创建一个需要存储的对象，这里我就直接使用User这个对象
```
public class User extends BaseEntity implements Serializable {
    @Column
    private String username;
    @Column
    private String password;
//get set 省略
```
这个配置类非必要，如过出现了jedis connect refused，排除了redis 配置的 #bind 127.0.0.1 等配置问题仍然无效, 这个配置可能有用，这个是指定jedis的链接地址和端口，默认的是连接本地的127.0.0.1：6379
```
@Configuration
@PropertySource(value = "classpath:/application.properties")
public class JedisRedisConfig {

    @Value("&{spring.redis.host}")
    private  String host;
    @Value("&{spring.redis.password}")
    private  String password;
    @Value("&{spring.redis.port}")
    private  int port;
    @Value("&{spring.redis.timeout}")
    private  int timeout;
    @Bean
    JedisConnectionFactory jedisConnectionFactory() {
        JedisConnectionFactory factory = new JedisConnectionFactory();
        factory.setHostName(host);
        factory.setPort(port);
        factory.setTimeout(timeout); //设置连接超时时间
        return factory;
    }
}
```
自定义redis的对象序列化和反序列化方法RedisObjectSerializer
```
public class RedisObjectSerializer implements RedisSerializer<Object> {
    private Converter<Object, byte[]> serializer = new SerializingConverter();
    private Converter<byte[], Object> deserializer = new DeserializingConverter();

    static final byte[] EMPTY_ARRAY = new byte[0];

    public Object deserialize(byte[] bytes) {
        if (isEmpty(bytes)) {
            return null;
        }
        try {
            return deserializer.convert(bytes);
        } catch (Exception ex) {
            throw new SerializationException("Cannot deserialize", ex);
        }
    }

    public byte[] serialize(Object object) {
        if (object == null) {
            return EMPTY_ARRAY;
        }
        try {
            return serializer.convert(object);
        } catch (Exception ex) {
            return EMPTY_ARRAY;
        }
    }

    private boolean isEmpty(byte[] data) {
        return (data == null || data.length == 0);
    }
}
```
最后是RedisTemplate实例方法
```
@Configuration
public class RedisConfig {
    @Bean
    JedisConnectionFactory jedisConnectionFactory() {
        return new JedisConnectionFactory();
    }

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<String, Object>();
        template.setConnectionFactory(jedisConnectionFactory());
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new RedisObjectSerializer());
        return template;
    }
}
```
最后运行测试用例实现redis的存储，(这里我遇见了一个问题，默认的序列化后对象在redis中是乱码的,因为我们项目中的对象是以JSON的格式存储到redis中的，等我继续研究哦)
```
	@Autowired(required = true)
    private RedisTemplate redisTemplate;
    @Test
    public void testSave(){
	// 保存对象
        User user = new User();
        user.setUsername("1");
        user.setPassword("2");
        redisTemplate.opsForValue().set(user.getUsername(), user);
		//获取对象并发现返回的对象结果正确
        Object object = redisTemplate.opsForValue().get( "1" );
        System.out.println(object.toString());
    }
```
emmm,我有了一个猥琐的想法，可以使用fastjson将对象转成JSON,在使用stringRedisTemplate将json存放到redis中，想到就试了试
```
	@Autowired
    private StringRedisTemplate stringRedisTemplate;
	
	 @Test
    public void testString(){
        User user = new User();
        user.setUsername("1");
        user.setPassword("2");
        stringRedisTemplate.opsForValue().set( user.getUsername(),user.toString() );
    }
```
这个时候的确redis内存放的是JSON字符
![](/bbb.png)
but.....,然后发现了在redis的序列化的时候其实是可以指定序列化的方式的,所以如果不需要自定义特殊的序列化方式，就直接使用jackson,对了配置文件也只写着一个就行了。
```
 @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<String, Object>();
        template.setConnectionFactory(jedisConnectionFactory());

        //jackson的序列方式
        Jackson2JsonRedisSerializer jackson2JsonRedisSerializer = new Jackson2JsonRedisSerializer(Object.class);
        ObjectMapper om = new ObjectMapper();
        om.setVisibility( PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        om.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
        jackson2JsonRedisSerializer.setObjectMapper(om);
        //string的序列方式
        StringRedisSerializer stringRedisSerializer = new StringRedisSerializer();
        //key值按String的方式
        template.setKeySerializer(stringRedisSerializer);
        //value 以json的方式
        template.setValueSerializer(jackson2JsonRedisSerializer);
        template.afterPropertiesSet();
        return template;
    }
```

# spring boot 1.x  redis 的注解使用
spring boot 使用注解的方式开启缓存，首先是配置缓存的配置文件类
```
@Configuration
@EnableCaching
public class CacheConfig extends CachingConfigurerSupport {

    @SuppressWarnings("rawtypes")
    @Bean
    public CacheManager cacheManager(RedisTemplate redisTemplate) {
        RedisCacheManager rcm = new RedisCacheManager( redisTemplate );
        // 多个缓存的名称,目前只定义了一个
        rcm.setCacheNames( Arrays.asList( "thisredis" ) );
        //设置缓存过期时间(秒)
        rcm.setDefaultExpiration( 600 );
        return rcm;
    }

    @Bean
    public RedisTemplate<String, String> redisTemplate(RedisConnectionFactory factory) {
        StringRedisTemplate template = new StringRedisTemplate( factory );
        Jackson2JsonRedisSerializer jackson2JsonRedisSerializer = new Jackson2JsonRedisSerializer( Object.class );
        ObjectMapper om = new ObjectMapper();
        om.setVisibility( PropertyAccessor.ALL,JsonAutoDetect.Visibility.ANY );
        om.enableDefaultTyping( ObjectMapper.DefaultTyping.NON_FINAL );
        jackson2JsonRedisSerializer.setObjectMapper( om );
        template.setValueSerializer( jackson2JsonRedisSerializer );
        template.afterPropertiesSet();
        return template;
    }

//这个是因为默认的JedisConnectionFactory是本地的redis,我链接的是我服务器上的配置，所以要手动配置一下
    @Bean
    JedisConnectionFactory jedisConnectionFactory() {
        JedisConnectionFactory factory = new JedisConnectionFactory();
        factory.setHostName("xx.xxx.xx.xx");
        factory.setPort(6379);
        factory.setTimeout(0); //设置连接超时时间
        return factory;
    }
}
```
这个时候启动服务就没有问题，接下来就编写缓存的方法还有测试类,这个方法指定了缓存名称，key是自定义的key值，condition 是配置当id不为3的时候将方法放入缓存中。
```
 @Cacheable(value = "thisredis",key="'users_'+#id"，condition="#id!=3")
    public String getUser(int id) {
        System.out.println( "Method executed.." );
        if (id == 1) {
            return "User 1";
        } else {
            return "User 2";
        }
    }
	
	@CacheEvict(value="thisredis", key="'users_'+#id",condition="#id!=1")
    @PostMapping("/delUser")
    public void delUser(Integer id) {
        // 删除user
		System.out.pringln("缓存删除")；
    }

```
|属性名称|描述|示例|
|-| :- | :-: |
|methodName|当前方法名|#root.methodName|
|targetClass|当前被调用的对象的class|#root.targetClass|
|caches|当前被调用的方法使用的Cache|#root.caches[0].name|
编写测试用例
```
 public static void main(String[] args) {
        AnnotationConfigApplicationContext ctx = new AnnotationConfigApplicationContext();
        ctx.register( CacheConfig.class );
        ctx.refresh();
        User user = ctx.getBean(User.class);
        System.out.println(user.getUser( 1 ));
        System.out.println(user.getUser( 1 ));
        System.out.println(user.getUser( 2 ));
        ctx.close();
    }
```
在getUser方面里面添加断点，可以发现在第二次调用user.getUser( 1 )时没有进入断点，而在调用user.getUser( 2 )进入了断点，因为在第二次user.getUser( 1) 的时候数据是从缓存中取出的，而调用delUser的时候会删除缓存区中key相同的数据






	
