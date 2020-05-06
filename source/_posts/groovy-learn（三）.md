---
title: groovy-learn（三）
date: 2019-05-22 00:32:56
tags: [java工具,gradle，groovy]
type: "categories"
categories: gradle
---
# groovy的高级操作
## 对json的操作
```
//列表转换成Json
def list = [new Person(name: 'david',age: 13),new Person(name: 'jane',age: 43)]
println JsonOutput.toJson(list)

//转换Object
def jsonSlpuer = new JsonSlurper()
//jsonSlpuer.parse()

//模拟发送请求和数据转换
def getNetworkDate(String url){
    //发送http请求
    def connection = new URL(url).openConnection()
    connection.setRequestMethod("GET")
    connection.connect()
    def response = connection.content.text
    //将json转对象
    def jsonSlpuer = new JsonSlurper()
    return jsonSlpuer.parseText(response)
}

def response = getNetworkDate('')
println response.data.head.name
```
# groovy对xml文件的处理
解析XML文件
![](/xmlString.png)
```
def xml = ''' '''
def xmlSluper = new XmlSlurper()
def result = xmlSluper.parseText(xml)
println result.value.books[0].book[0].title.text()
println result.value.books[0].book[0].@avaliable

//根据作者赛筛选数据
def bookList = []
result.value.books.each{ books->
    books.book.each{ book->
        def author = book.author.text()
        if(author.equals("李刚")){
            bookList.add(book.title.text())
        }
    }
}

//深层遍历
def titles = result.depthFirst().findAll {book->
    return book.author.text() == '李刚'? true :false

}
//创建XML
def sw = new StringWriter()
def xmlBuilder = new MarkupBuilder(sw)
xmlBuilder.langs(type:'current'){
    language(flavor:'static')
    language(flavor:'public')
    language(flavor:'private')
}

println sw
```
# groovy 对文件的处理
```
//读取文件
def file = new File('../../helloGroovy.iml')
file.eachLine {line->
    println line
}
打印出全部的文件信息
println file.text
打印一部分文件的信息
def  reader = file.withReader {reader->
    char[] buffer = new char[100]
    reader.read(buffer)
    return buffer
}
println reader

def copy(String sourcePath,String destationPath){
    def desFile = new File(destationPath)
    if(!desFile.exists()){
        desFile.createNewFile()
    }
    //copy
    new File(sourcePath).withReader {reader->
        def lines = reader.readLines()
        desFile.withWriter {writer->
            lines.each {line->
                writer.append(line)
            }
        }
    }
    return true
}
def copy = copy('../../helloGroovy.iml','../../helloGroovy2.iml')
//测试存/读取对象
def saveObject(Object obj,String path){
    try{
        def desFile = new File(path)
        if(!desFile.exists()){
            desFile.createNewFile()
        }
        desFile.withObjectOutputStream {out->
            out.writeObject(obj)
        }
        return true
    }catch(Exception e){
        e.printStackTrace()
        reutrn false
    }
}
def readObject(String path){
    def obj = null
    try{
        def file = new File(path)
        if(file == null || !file.exists()){return null}
        //文件中读取对象
        file.withObjectInputStream {input->
            obj=input.readObject()
        }
    }catch (Exception e){

    }
    return obj
}
//测试
def person = new Person(name: "david",age:17)
//saveObject(person,'../../person.bin')
def result = (Person)readObject('../../person.bin')
println  "name: ${result.name},age:${result.age}"
```


