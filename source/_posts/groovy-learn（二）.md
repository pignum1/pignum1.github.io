---
title: groovy-learn（二）
date: 2019-05-20 22:33:16
tags: [java工具,gradle，groovy]
type: "categories"
categories: gradle
---
# groovy中的数据结构
## groovy中列表的操作
```
//列表
//def list = new ArrayList(); java中定义列表的方式
def list = [1,2,3,4,5]
//println list.class
//println list.size()

//定义数组的方式
//def array = [1,2,3,4,5] as int[]
//int[] array2 = [1,2,3,4,5]

//对列表进行排序
def sortList = [5,9,3,5,-2]
//Collections.sort(sortList)
Comparator comparator = {
    a,b-> Math.abs(b)>Math.abs(a) ? 1 :  -1  //比较的逻辑和结果是反的？？？
}
Collections.sort(sortList,comparator)
println  sortList

def strList = ['sd','ddqw','qwefcf','a']
strList.sort{it->return it.size()}

//列表的查找
def findList = [1,6,9,4,11]
//int result = findList.find {
//    return it%2==0
//}
//def result = findList.findAll {
//    return it%2!=0
//}
//def result = findList.min{return Math.abs(it)}
//def result = findList.max{return Math.abs(it)}
//def result = findList.count {return it>10}
//println result

//list的元素添加
findList.add(8)
findList.leftShift(7)
findList<<13
//println findList

//list的删除操作
findList.remove(7)//移除下标的元素
findList.remove((java.lang.Object) 7)//移除元素
println findList
```
## groovy中的映射
map在groovy中的定义
```
//map的定义
def colors = [red:'ff00000',green:'00ff00',blue:'0000ff']
//map查询
//println colors['red']
//println colors.red
//添加元素
colors.yellow = 'ffff00'
//println colors.toMapString( )

//map的遍历
def stu = [1:[num:'001',name:'boa',score:11],
           2:[num:'002',name:'bob',score:57],
           3:[num:'003',name:'boc',score:89],
           4:[num:'004',name:'bod',score:94]
            ]
stu.each {
    def student->
        println "the key is ${student.key},the value is ${student.value}"
}
//直接遍历key ,value
stu.eachWithIndex{ key,value,index ->
    println "the key is ${key},the value is ${value} index is ${index}"
}

//map中的查找
def entry = stu.find {def student ->return student.value.score>60}
//println  entry

def names = stu.findAll {def student ->return student.value.score>60}.collect {return it.value.name}
//println names

//map的排序
def sort = stu.sort {def stu1,def stu2 ->
    Number score1 = stu1.value.score
    Number score2 = stu2.value.score
    return score1 == score2 ? 0 :score1<score2? -1: 1
}
println  sort
```
## groovy中的范围
```
//定义范围
def range = 1..10

println range[0]//获取范围中的元素,取第一个数
println range.contains(7)//判断是否包含某个元素
println range.from//起始值
println range.to//中止值
//遍历
range.each {
    println it
}
//范围的应用
def getGrade(Number number) {
    def result
    switch (number) {
        case 0..60:
            result = "不及格"
            break
        case 61..100:
            result = "及格"
            break
    }
    println result
}
getGrade(71)
```
# groovy中的面向对象类，接口的使用
创建 new Groovy Class
```
// 默认为class
// 默认继承groovyObject类
class Person {
    String name;

    Integer age;

    def increaseAge(Integer year){
        age += year;
    }

}
```
创建groovy的脚本 groovy script类型 objectstu 
操作对象的属性和方法
```
Person person = new Person(name: 'david',age: 22)
println "person's name is ${person.name} .person's age is ${person.age}"
person.increaseAge(12)
person.play()
person.eat()
```
创建groovy中的接口
```
 //接口中的方法只能是public
interface Action {
    def eat()
    def drink()
    def play()
}
```
Trait类似Interface,可以定义默认的实现方法，java8中也能配置接口默认实现方法
```
trait DefaultAction {
    abstract void eat()
    void play(){
        println "play"
    }
}
```
# 元编程
groovy中方法的调用顺序如图
![](/yuan.png)
```
println person.cry()
```
会报错groovy.lang.MissingMethodException: No signature of method
重写Person类中的invokeMethod方法
```
/**
 * 一个方法寻找不到调用此方法
 */
    @Override
    Object invokeMethod(String s, Object o) {
        return "method name is ${s},param is ${o}"
    }
```
再次运行程序打印方法名称和参数
同理也可以重写methodMissing方法
```
    def methodMissing(String name,Object args){
        return "method2 name is ${name},param is ${args}"
    }
```
## metaClass的使用

```
为类动态新增一个属性 
Person.metaClass.sex = 'male'
Person p1 = new Person(name: 'jane',age: 23)
println p1.sex
//为类动态生成方法
Person.metaClass.upper = {->sex.toUpperCase()}
println p1.upper()
//生成静态方法
Person.metaClass.static.createPerson={String name,Integer age->new Person(name:name,age:age)}
Person p2 =  Person.createPerson("test",3)
println p2.name+" and "+p2.getAge()
```
如果想要注入的方法或者属性全局可用
在外部的注入方法前添加
ExpandMetaClass.enableGlobally()






