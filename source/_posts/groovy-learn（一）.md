---
title: groovy learn（一）
date: 2019-05-19 12:58:59
tags: [java工具,gradle，groovy]
type: "categories"
categories: gradle
---
# 一、groovy 的环境安装
centos下的安装
```
$ curl -s get.sdkman.io | bash
$ source "$HOME/.sdkman/bin/sdkman-init.sh"
$ sdk install groovy
$ groovy -version
```
windows下的安装
官网下载安装包后解压，配置环境
•新建GROOVY_HOME，值为解压后文件的路径。
![](/groovy_home.png)
•修改PATH，在最后追加<code>%GROOVY_HOME%\bin
![](/home.png)
#二 groovy的基础语法
groovy的变量
![](/type.png)
创建.Groovy Script文件
```
package variable
//groovy 中变量最后都会被包装成对象类型
int x = 10
println x.class  //Integer
double  y = 1.14
println y.class  // Double

//groovy 定义变量的类型,使用def快速定义弱类型,推断数据类型
def x_1 =2
println x_1.class
def y_1 = 3.15
println y_1.class
def name = 'david'
println name.class
```
# 三、groovy中的字符串用法
```
def str = 'a \'a\' string '
println str
println str.class

//三个引号定义的字符串可以指定格式
def thupleStr = '''\
three 
signle 
string'''
println thupleStr
println  thupleStr.class

//双引号字符串格式,可一再字符串中引用其他字符串，引用其他变量后类型是groovy.runtime.GStringImpl
def name =  "david"
def doubleName = "name: ${thupleStr}"
println doubleName
println doubleName.class

//双引号中的扩展接受任意的表达式
def sum = "the sum of 2 and 3 equals ${2 + 3}"
println sum

//测试GString 和String 的转换.编译器转换
def result = echo(sum)
println result
println result.class
String echo(String message){
    return message
}

/*******字符串String 常用方法 *********************/


def str1 = "justTest"
//println st1.center(9,'a')//字符串两边填充字符，默认填充空格。先右后左

//println str1.padLeft(10,'a')//字符串右侧填充

//字符串比较
def str2 = "hello"
println str1>str2

println str2[0]  //获取下标的值
println str2[0..3]  //获取下标范围的值

println str2.minus("ello")   //等同于 石str1 - str2

println str2.reverse() //字符串反转

println str2.capitalize()  //首字母大写
```
# 四、groovy中的逻辑控制
```
 package variable
//逻辑控制

// switch语句
 def x = 1.23
 def result
 switch (x){
    case 'foo':
        result="founf foo"
        break
     case 'bar':
         result = 'bar'
         break
     case [1.23,5,6,'inList']: //列表中的结果匹配
         result = 'list'
         break
     case 12..30:
         result = 'range'
         break
     case Integer:
         result = 'integer'
         break
     case BigDecimal:
         result = 'bigDecimal'
         break
     default:result = 'default'
 }

 println result

// for循环  计算0-9的和
def sum = 0
 for(i in 0..9){
     sum+=i
 }
 println 'sum:'+sum

 //对于List中元素循环
 def sum1 = 0
 for(i in [1,2,3,4,5,6,7,8,9]){
     sum1 += i
 }
 println "sum1:"+sum1

// 对MAP进行循环
 def sum2 =0
 for(i in ['xiaoMing':1,'xiaoQiang':2,'xiaoHua':3]){
     sum2 += i.value
 }
 println 'sum2:'+sum2
```
# 五、闭包
![](/close.png)
##闭包的定义
闭包是代码块。定义如下
```
//*******闭包的定义和参数********
def closure = {println  "close package"}//闭包的定义方式
closure.call()//调用闭包方法的两种方式
//closure()

def close = {String name -> println "hello ${name}"}//有参数的闭包定义
close("david")

//多个参数
def close1 = {String name,Integer age-> println "hello :${name}&${age}"}
close1("pangpang",12)

//闭包方法的隐式参数it
def close2 = { println "hello ${it}"}
close2("david")

//*********闭包的返回值**********
def close3 = { println  "test return ${it}"}
def result = close3("test")
println result //闭包方法必定有返回值，默认返回null
```
## 闭包的用法
![](/closeuse.png)
```
//闭包求阶乘
int fab(number){
    int result = 1
    1.upto(number,{num->result *=num})//upto 实现循环阶乘
    return result
}
println "向上阶乘："+fab(5)

int fab2(int number2){
    int result = 1
    number2.downto(1,{num->result *=num})
    return  result
}
println "向下阶乘："+fab2(7)

//累计求和方法,这里的次数由0开始，所以不能用于阶乘的计算
int cal(int number){
    int sum = 0
    number.times{ num->sum+=num }
    return sum
}

println cal(101) // 计算0-100的结果


//*********字符串在闭包的使用
String str ="string test 1"
str.each {
//    String result -> print result.multiply(2)  //每个字符串输出两次
}

//查找满主条件的第一个元素
str.find{
    String s->s.isNumber()  //必须是一个返回布尔类型的闭包
}

//查找满主条件的所有元素
def list = str.findAll{
    String s -> !s.isNumber()
}
println "列表："+list.toListString()

//判断字符串是否满足某个条件
def res = str.any {
    String s-> s.isNumber()
}
println "res:"+res

//是否每一项满足某个条件
println "every:"+str.every {String s-> s.isNumber()}

//对字符串中每一项处理
def list2 = str.collect {
    it.toUpperCase()
}
println "list2:"+list2.toListString()
```
## 闭包的三个重要变量
this、owner、delegate三个关键字
this代表定义闭包的类。
owner代表闭包定义处的类或者对象，闭包内部定义闭包中的owner是外层的闭包
deleGate 代表任意的对象，默认值就是owner
如果在类或者方法中定义闭包，此时this,owner,deleGate是一样的，指向闭包定义处的实例或者类本身
如果在闭包中定义闭包，this指向的仍然是闭包处的实例或者类本身，而owner和deleGate指向的最近的闭包对象。
```
 //定义一个内部类 , 三个变量指向最近的封闭类
class Person{
    def classClosure = {
        println "classClouser this"+this
        println "classClouser this"+owner
        println "classClouser this"+delegate
    }

    def say(){
        def methodClosure = {
            println "methodClouser this"+this
            println "methodClouser this"+owner
            println "methodClouser this"+delegate
        }
        methodClosure.call()
    }
}

Person person = new Person()
person.classClosure.call()
person.say()

//在闭包中中定义闭包
def nestClouser = {
    def innerClouser = {
        println "innerClouser this"+this
        println "innerClouser this"+owner
        println "innerClouser this"+delegate
    }
    innerClouser.delegate = person // 修改默认的deleGate.此时deleGate指向person对象

    innerClouser.call()
}
//this 指向实例本身或者定义处的类，owner和deleGate表示的是距离最近的闭包
nestClouser.call()
```
## 闭包的委托策略
```
//委托构造
class Student{
    String name
    def pretty = {
        println "my name is ${name}"
    }

    String toString(){
        pretty.call()
    }
}

class Teacher{
    String name
}
Student student = new Student(name: "jane")
Teacher teacher = new Teacher(name: "lay")
student.toString();
student.pretty.delegate = teacher // 将闭包中的delegate指向teacher
student.pretty.resolveStrategy = Closure.DELEGATE_FIRST  //修改委托策略为 deleGate 默认是owner
student.toString()  //此时会在委托的类中寻找name属性，找不到会回来本身类的内部寻找
```

