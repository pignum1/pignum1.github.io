---
title: gradle学习（二）
date: 2019-05-09 23:55:18
tags: [java工具,gradle]
type: "categories"
categories: gradle
---
# gradle的生命周期

![][/yilai.png]
gradle的生命周期监听
gradle 的生命周期主要分为三个阶段：
@nesp;@nesp;@nesp;@nesp;项目的初始化阶段，构建Project项目的project对象	
@nesp;@nesp;@nesp;@nesp;解析所有projiect中的task,并构建task的拓扑图
@nesp;@nesp;@nesp;@nesp;执行相关的task和相关的task

项目的目录结构如下图所示
![](/content.png)
全局的build.gradle中添加监听方法
```
//声明gradle脚本自身需要的资源，可以声明的资源包括依赖项、第三方插件、maven仓库地址等
buildscript{}
// 所有子项目的通用配置
subprojects {}
//所有项目的通用配置
allprojects{}

//初始化阶段后，配置阶段开始前的
this.beforeEvaluate {}

//配置阶段完成，执行阶段前
this.afterEvaluate {
    println "配置完成"
}

//gradle生命周期完成之后
this.gradle.buildFinished {
    println "执行完成"
}
在setting.gradle中添加
println "初始化开始"
```
再运行gradle中的task就会打印出上述的打印语句
##  gradle中的project
在gradle多项目中，除了根工程，这些Moudle也是gradle的工程，而文件中的build.gradle标志Moudle是gradle项目
执行gradle projects命令，可以看见打印出
![](/projects.png)
project以树的结构管理项目，但是项目一般只构建两层
gradle的相关API大致可以分为下图中的六部分
![](/projects.png)
### project中的API
在根project的build中定义打印处所有project的方法，并调用，可以直接在命令窗口上任意运行task，因为都会加载配置文件，执行this.getProjects()在加载配置文件中就运行。
```
//加载配置文件时会调用
this.getProjects()
//返回所有的project列表
def getProjects(){
    println "--------"
    println "root project"
    println "--------"
    this.getAllprojects().eachWithIndex{ Project project, int i ->
        if(i==0){
            println "rootProject:${project.name}"
        }else {
            println "+-- :${project.name}"
        }
    }
}
```
同理，还可以定义获取父project和根project的方法，但是这获取父project方法不能再根目录下的build中运行，因为根目录没有父project了
```
//获取父project的名称
def getParentName = {
    println this.getParent().name
}
//获取根目录的名称
def getRootName ={
    println this.getRootProject().name
}
//相当于设置对应模块的配置，不过通用模块可以在subprojects{}里面配置的
project('webOne'){
    Project project-> println project.name
        apply plugin: 'io.spring.dependency-management'
        agroup 'com.demo'
}
```
### 属性相关的API
geadle中的Project中的默认配置如下
```
public interface Project extends Comparable<Project>, ExtensionAware, PluginAware {
	//默认的配置文件名称是build.gradle，
    String DEFAULT_BUILD_FILE = "build.gradle";
	//默认的路径分割符
    String PATH_SEPARATOR = ":";
	//gradle的默认输出文件夹
    String DEFAULT_BUILD_DIR_NAME = "build";
	//配置常量文件名
    String GRADLE_PROPERTIES = "gradle.properties";
    String SYSTEM_PROP_PREFIX = "systemProp";
    String DEFAULT_VERSION = "unspecified";
    String DEFAULT_STATUS = "release";
	...
}
```
在build.gradle中定义扩展属性和定义版本
```
//定义扩展属性
ext {
	set('springCloudVersion', "Greenwich.SR1")
}
//使用扩展的属性
dependencyManagement {
	imports {
		mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
	}
}
```
如果想在所有的子项目中都定义某些属性，可以在subProjects{}中编写ext{},或是在build.gradle中添加属性，在子项目的build.gradle文件中使用${}去获取对应的值。
在根目录下的settings.gradle,gradle.properties中控制是否添加webOned,然后刷新gradle，idea会提示webOne移出Gradle,而且树状结构也没有了webOne
```
//gradle.properties中
isLoadOne= fasle

//在settings.gradle中添加
rootProject.name = 'myGradleProject'
include 'webTwo'
if(hasProperty('isLoadOne')?isLoadOne.toBoolean():false{
	include 'webOne'
}
```
### 文件操作属性API
获取文件相关的API
```
//获取跟工程的根路径
println "root path :"+ getRootDir().absolutePath
//build文件的路径
println "build path:"+getBuildDir().absolutePath
//当前project路径
println  "project path:"+getProjectDir().absolutePath

//在build.gradle找到对应路径的文件，并打印出内容
def getContent(String path){
    try{
	//file方法从当前project的路径开始寻找，files（）方法参数是多个路径，返回的参数是file的集合
        def file = file(path)
        return file.text
    }catch (Exception e){
        println "error"
    }
}

println getContent('build.gradle')
```
gradle的文件拷贝在webOne中新建一个文件copy.txt,webOne的build中添加下面的代码
```
copy {
	from('copytest.txt')
	into getRootProject()
	//不拷贝某些文件
	exclude{}
	//拷贝后重命名
	rename{}
}
```
在执行gradle的同步后就会在build文件夹下生成对应的文件，
文件树的遍历
```
//对文件树的遍历
fileTree('webTwo/src') { FileTree fileTree->
    fileTree.visit {FileTreeElement fileTreeElement->
        println "the file name is :"+fileTreeElement.file.name

    }
}

```
### 依赖相关的API
buildscript 是项目的配置，常用通过的是repositories仓库的配置和dependencies依赖
```
buildscript{ ScriptHandler scriptHandler->
    //配置工程的仓库地址
  repositories{
        //私有仓库,如果多个就继续配下去
        maven {
            //仓库的别名
            name 'person'
            //maven仓库地址
            url 'hhttp://localhoys......'
            //配置仓库的账号和密码
            credentials{
                username = 'admin'
                password = 'admin123'
            }

        }
        mavenCentral()
        //本地maven库
        mavenLocal()
        jcenter()

    }
    //配置工程的插件依赖地址
    dependencies{
        //gradle需要的依赖
        classpath 'com.android.tools.build:gradle:2.2.2'
        classpath 'com.tencent.tinker-patch-gradle-plugin:1.7.7'//腾讯的热修复框架
        //poject需要的依赖
        compile （group: 'net.officefloor.server', name: 'officeserver', version: '3.10.3‘）{
		//这个常用于解决依赖重复的冲突
		exclude module:'support-v4'
        //添加依赖的工程，引用project
        compile project('webOne')
    }

}
```








