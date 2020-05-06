---
title: gradleThree
date: 2019-07-28 10:06:27
tags: [java工具,gradle，groovy]
type: "categories"
categories: gradle
---
# Task任务
## task任务定义
在gradle文件中定义task的方法有两种，如下。
```
//直接定义task
task hello1(group: 'immoc',description: 'hellostudy'){
    println "hello1";
}


//通过TaskContainer 创建task
this.tasks.create(name: 'hello2'){
    setGroup('immoc');
    setDescription('hellostudy')
    println "hello2"
}
```
在执行gradle clean时，两个任务都会配置阶段运行。配置task在运行阶段而不是配置阶段,doFirst和doLast，可以监听任务执行的时长，代码如下、
```
task test(){}
def startBuildTime ,endBuildTime;
//计算构建的时常
this.afterEvaluate {Project project->
    //保证配置阶段完成
    def preBuildTask = project.tasks.findByName('test')
    preBuildTask.doFirst {
        startBuildTime =System.currentTimeMillis();
        println "start time is ${startBuildTime}"
    }
    def buildTask = project.tasks.findByName('test')
    buildTask.doLast {
        endBuildTime = System.currentTimeMillis();
        println "end time is ${endBuildTime}"
        println "cost time is ${endBuildTime- startBuildTime}ms"
    }
}
```
## task的执行顺序
task的执行顺序可以分成三种：dependsOn强依赖的方式、通过task输入输出指定、通过API指定顺序
强依赖的方式执行顺序,先执行依赖的task
```
 task taskX(){doLast { println "task x"}}
task taskY(){doLast { println "task y" }}
task taskZ(dependsOn: [taskX,taskY]){
    doLast {println "task z"}
}
另一种指定依赖写法
taskZ.denpendsOn(taskX,taskY)
```
另一种动态的指定执行顺序的方法,调用dependsOn方法动态添加依赖，注意被依赖的方法要定义在需要引用的task之前
```
// <<等同于 doLast,不在编译期执行
task lib1 << {
    println "lib1"
}
task lib2 << {
    println "lib2"
}
task noLib  << {
    println "noLib"
}

task testLib {
//    添加前缀名为lib的依赖
    dependsOn this.tasks.findAll {
        task->return task.name.startsWith('lib')
    }
    doLast {
        println 'test'
    }
}
```
## task 的输入和输出
//TODO 

## task的指定顺序
使用mustRunAfter 来指定任务的执行顺序,控制台输入gradle task1 task3 task2，可以发现任务执行顺序是1、2、3
如果使用的是shouldRunAfter 执行顺序不是强制性
``` 
task task1{
    doLast {
        println "task1"
    }
}
task task2{
    mustRunAfter task1
    doLast {
        println "task2"
    }
}
task task3{
    mustRunAfter task2
    doLast {
        println "task3"
    }
}
```
## task自定义和配置
在定义task的时候可以设置task的分组和描述，idea中gradle中的任务就是按分组分类，默认为other下的task
```
task helloTask{
    println "helloTask"
}
//通过TaskContainer创建任务
this.tasks.create(name: 'helloTask2'){
	//给任务添加属性
	setGroup("gradle")
    setDescription("helloTask2")
    println "helloTask2"
}
```
```
设置资源文件夹
sourceSets{
	main {
		groovy {
			others{
				srcDir 'src/main/others'
			}
		}
	}
}
```

