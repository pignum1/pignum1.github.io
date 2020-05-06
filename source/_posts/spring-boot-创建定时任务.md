---
title: spring-boot 创建定时任务
date: 2019-08-19 23:40:35
tags: [schedule ,spring boot ]
type: "categories"
categories: spring boot
---
# 使用注解@Scheduled创建定时任务
@Scheduled默认创建的线程是单线程，任务的执行会受到上一个任务的影响，创建定时任务也比较简单
```
@Component
@Configuration      //1.主要用于标记配置类，兼备Component的效果。
@EnableScheduling   // 2.开启定时任务
public class ScheduledTask {
    //3.添加定时任务
    @Scheduled(cron = "0/5 * * * * ?")
    //或直接指定时间间隔，例如：5秒
    //@Scheduled(fixedRate=5000)
    private void configureTasks() {
        System.err.println("执行静态定时任务时间: " + LocalDateTime.now());
    }
}
```
Cron的表达式为 秒（0-59） 分（0~59）时（0~23）日（0~31）的某天，需计算月（0~11）周几（ 可填1-7 或 SUN/MON/TUE/WED/THU/FRI/SAT）
"0/5 * * * * ?"可以解析成 每5秒执行一次，其他不指定，此时开启application,控制台没隔5秒打印一次
# 基于接口的定时任务
```
@Component
@Configuration      //1.主要用于标记配置类，兼备Component的效果。
@EnableScheduling   // 2.开启定时任务
public class DynamicScheduleTask implements SchedulingConfigurer {

    @Override
    public void configureTasks(ScheduledTaskRegistrar taskRegistrar) {
        taskRegistrar.addTriggerTask(
                //1.添加任务内容(Runnable),匿名
                () -> System.out.println("执行动态定时任务: " + LocalDateTime.now().toLocalTime()),
                //2.设置执行周期(Trigger)
                triggerContext -> {
                    return new CronTrigger("0/5 * * * * ?").nextExecutionTime(triggerContext);
                }
        );
    }
}
```
# 多线程的定时任务
```
@Component
@EnableScheduling   // 1.开启定时任务
@EnableAsync        // 2.开启多线程
public class MultiThreadScheduleTask {

    @Async
    @Scheduled(fixedDelay = 1000)  //间隔1秒
    public void first() throws InterruptedException {
        System.out.println("第一个定时任务开始 : " + LocalDateTime.now().toLocalTime() + "\r\n线程 : " + Thread.currentThread().getName());
        System.out.println();
        Thread.sleep(1000 * 10);
    }

    @Async
    @Scheduled(fixedDelay = 2000)
    public void second() {
        System.out.println("第二个定时任务开始 : " + LocalDateTime.now().toLocalTime() + "\r\n线程 : " + Thread.currentThread().getName());
        System.out.println();
    }
}
```
这个定时任务随着时间的增加不断的增加线程，这肯定会消耗大量的资源，因此在配置多线程的定时任务时，常常需要设置一个线程池来避免资源消耗过多
```
@EnableAsync
@Configuration
public class TaskPoolConfig {
    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(200);
        executor.setKeepAliveSeconds(60);
        executor.setThreadNamePrefix("taskExecutor-");
        executor.setWaitForTasksToCompleteOnShutdown(true);//设置线程在任务执行完之后才x释放
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        return executor;
    }
}
```
使用Future来获取Runable的执行结果
```
@Slf4j
@Component
public class Task {
    public static Random random = new Random();
    @Async("taskExecutor")
    public Future<String> run() throws Exception {
        long sleep = random.nextInt(10000);
        log.info("开始任务，需耗时：" + sleep + "毫秒");
        Thread.sleep(sleep);
        log.info("完成任务");
        return new AsyncResult<>("test");
    }
}
```
定义超时时间并释放线程
```
@Slf4j
@RunWith(SpringJUnit4ClassRunner.class)
@SpringBootTest
public class ApplicationTests {
    @Autowired
    private Task task;
    @Test
    public void test() throws Exception {
        Future<String> futureResult = task.run();
        String result = futureResult.get(5, TimeUnit.SECONDS);
        log.info(result);
    }
}
```

