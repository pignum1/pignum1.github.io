---
title: java IO与NIO的区别（一）
date: 2019-04-15 17:03:35
tags: [java基础,io/nio]
type: "categories"
categories: java NIO
---
# 一、概念
NIO即New IO，这个库是在JDK1.4中才引入的。NIO和IO有相同的作用和目的，但实现方式不同，NIO主要用到的是块，所以NIO的效率要比IO高很多。在Java API中提供了两套NIO，一套是针对标准输入输出NIO，另一套就是网络编程NIO。
# 二、IO和NIO的对比区别
| IO|NIO|
| :-: | :-: |
|面向流|面向缓冲|
|阻塞IO|非阻塞IO|
|无|选择器|
## 1、面向流与面向缓冲
面向流的IO从流中读取一个或多个字节，直至读取完所有的字节，。此外，它不能前后移动流中的数据。如果需要前后移动从流中读取的数据，需要先将它缓存到一个缓冲区。Java NIO的缓冲导向方法略有不同。数据读取到一个它稍后处理的缓冲区，需要时可在缓冲区中前后移动。还需要检查是否该缓冲区中包含所有您需要处理的数据。而且，需确保当更多的数据读入缓冲区时，不要覆盖缓冲区里尚未处理的数据。
## 2、阻塞IO与非阻塞IO
Java IO的各种流是阻塞的。当一个线程在执行read()或write()操作时，该线程被阻塞，直到有一些数据被读取，或数据完全写入。java NIO是非阻塞，使一个线程从某通道发送请求读取数据，但是它仅能得到目前可用的数据，如果目前没有数据可用时，就什么都不会获取，而不是保持线程阻塞，所以直至数据变的可以读取之前，该线程可以继续做其他的事情。线程通常将非阻塞IO的空闲时间用于在其它通道上执行IO操作，所以一个单独的线程现在可以管理多个输入和输出通道（channel）。
## 3、选择器
Java NIO的选择器允许一个单独的线程来监视多个输入通道，你可以注册多个通道使用一个选择器，然后使用一个单独的线程来“选择”通道：这些通道里已经有可以处理的输入，或者选择已准备写入的通道。这种选择机制，使得一个单独的线程很容易来管理多个通道。
# 三、NIO与IO对程序设计的影响
使用NIO与IO的调用接口不同，使用NIO与IO的对比。
![](/streamAndThread.png)
{% codeblock %}
	Name: Anna 
	Age: 25
	Email: anna@mailserver.com 
	Phone: 1234567890
{% endcodeblock %}
以IO的方式逐行读取文本数据
```java
	InputStream input = ... ; // get the InputStream from the client socket   
	BufferedReader reader = new BufferedReader(new InputStreamReader(input));   
	String nameLine   = reader.readLine(); 
	String ageLine    = reader.readLine(); 
	String emailLine  = reader.readLine(); 
	String phoneLine  = reader.readLine();
```
以IO方式逐行读取每行的数据时，readLine()读取完数据之前，IO读取流被阻塞，所以第一个获取的是姓名信息，第二个readLine()获取的是年龄信息，能够确定每一步的读数据获取到的数据。以NIO的方式读取文本数据
```java
	ByteBuffer buffer = ByteBuffer.allocate(48); //
	int bytesRead = inChannel.read(buffer); 
```
在第二行中，冲通道读取字节到ByteBuffer。当这个方法调用返回时，你不知道你所需的所有数据是否在缓冲区内。你所知道的是，该缓冲区包含一些字节，这使得处理有点困难。假设第一次 read(buffer)调用后，读入缓冲区的数据只有半行，例如，“Name:An”，你能处理数据吗？显然不能，需要等待，直到整行数据读入缓存，所以，你怎么知道是否该缓冲区包含足够的数据可以处理呢？好了，你不知道。发现的方法只能查看缓冲区中的数据。其结果是，在你知道所有数据都在缓冲区里之前，你必须检查几次缓冲区的数据。这不仅效率低下，而且可以使程序设计方案杂乱不堪。例如：
```java
ByteBuffer buffer = ByteBuffer.allocate(48);   
int bytesRead = inChannel.read(buffer);   
while(! bufferFull(bytesRead) ) {   
       bytesRead = inChannel.read(buffer);   
}
```
bufferFull()方法必须跟踪有多少数据读入缓冲区，并返回真或假，这取决于缓冲区是否已满。换句话说，如果缓冲区准备好被处理，那么表示缓冲区满了。bufferFull()方法扫描缓冲区，但必须保持在bufferFull（）方法被调用之前状态相同。如果没有，下一个读入缓冲区的数据可能无法读到正确的位置。这是不可能的，但却是需要注意的又一问题。如果缓冲区已满，它可以被处理。如果它不满，并且在你的实际案例中有意义，你或许能处理其中的部分数据。但是许多情况下并非如此。下图展示了“缓冲区数据循环就绪”：
![](/buffer.png)
# 四、总结
NIO可以只使用一个（或几个）单线程管理多个通道（网络连接或文件），但付出的代价是解析数据可能会比从一个阻塞流中读取数据更复杂。如果需要管理同时打开的成千上万个连接，这些连接每次只是发送少量的数据，例如聊天服务器，实现NIO的服务器可能是一个优势。同样，如果你需要维持许多打开的连接到其他计算机上，如P2P网络中，使用一个单独的线程来管理你所有出站连接，可能是一个优势。一个线程多个连接的设计方案如下图所示：
![](/connection.png)