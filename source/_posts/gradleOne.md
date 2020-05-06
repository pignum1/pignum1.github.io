---
title: gradle学习（一）
date: 2019-05-08 23:13:49
tags: [java工具,gradle]
type: "categories"
categories: gradle
---
# 一、简介
Gradle是一种构建工具，它抛弃了基于XML的构建脚本，取而代之的是采用一种基于Groovy的内部领域特定语言。
在Gradle中，有两个基本概念：项目和任务
&ensp;&ensp;&ensp;&ensp;1.项目是指我们的构建产物（比如Jar包）或实施产物（将应用程序部署到生产环境）。一个项目包含一个或多个任务。
&ensp;&ensp;&ensp;&ensp;2.任务是指不可分的最小工作单元，执行构建工作（比如编译项目或执行测试）。
每一次Gradle的构建都包含一个或多个项目。
&ensp;&ensp;&ensp;&ensp;Gradle本身的领域对象主要有Project和Task。Project为Task提供了执行上下文，所有的Plugin要么向Project中添加用于配置的Property，要么向Project中添加不同的Task。一个Task表示一个逻辑上较为独立的执行过程，比如编译Java源代码，拷贝文件，打包Jar文件，甚至可以是执行一个系统命令或者调用Ant。另外，一个Task可以读取和设置Project的Property以完成特定的操作。
# 二、gradle的构建基础
&ensp;&ensp;&ensp;&ensp;构建第一个脚本。创建一个build.gradle的文件,运行CMD切换到build.gradle的文件目录，gradle的命令默认会在当前目录下寻找名未build.gradle的构建脚本。build.gradle
```
task hello {
    doLast {
        println 'Hello world!'
    }
}
```
运行命令gradle -q hello执行脚本，打印出  hello world
## 快速定义任务
采用闭包的方式来定义了一个叫做 hello 的任务
```
task hello << {
    println 'Hello world!'
}
```
gradle脚本也能使用groovy，在build.gradle中编辑
```
task upper << {
    String someString = 'mY_nAmE'
    println "Original: " + someString
    println "Upper case: " + someString.toUpperCase()
}
Output of gradle -q upper
> gradle -q upper
Original: mY_nAmE
Upper case: MY_NAME
```
## 任务依赖
在build.gradle中添加任务
```
task intro(dependsOn: hello) << {
    println "I'm Gradle"
}
task hello << {
    println 'Hello world!'
}
```
任务之间的依赖的声明顺序可以不不必为顺序声明
## 创建动态任务
```
4.times { counter ->
    task "task$counter" << {
        println "I'm task number $counter"
    }
}
```
通过 API 进行任务之间的通信 - 增加任务行为
```
task hello << {
    println 'Hello Earth'
}
hello.doFirst {
    println 'Hello Venus'
}
hello.doLast {
    println 'Hello Mars'
}
hello << {
    println 'Hello Jupiter'
}
Output of gradle -q hello
> gradle -q hello
Hello Venus
Hello Earth
Hello Mars
Hello Jupiter
```
## 增加自定义的属性
```
task myTask {
    ext.myProperty = "myValue"
}

task printTaskProperties << {
    println myTask.myProperty
}
//gradle -q printTaskProperties 的输出为
Output of gradle -q printTaskProperties
\> gradle -q printTaskProperties
myValue
```
## 定义默认任务
```
defaultTasks 'clean', 'run'
task clean << {
    println 'Default Cleaning!'
}
task run << {
    println 'Default Running!'
}
task other << {
    println "I'm not a default task!"
}
```
输出的结果
```
Output of gradle -q
\> gradle -q
Default Cleaning!
Default Running!
```
## Configure by DAG
```
task distribution << {
    println "We build the zip with version=$version"
}
task release(dependsOn: 'distribution') << {
    println 'We release now'
}
gradle.taskGraph.whenReady {taskGraph ->
    if (taskGraph.hasTask(release)) {
        version = '1.0'
    } else {
        version = '1.0-SNAPSHOT'
    }
}
\> gradle -q distribution
We build the zip with version=1.0-SNAPSHOT
```
使用钩子taskGraph来获取build.gradle定义运行时的版本信息
