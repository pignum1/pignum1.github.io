---
title: java-IOandNIO（二）
date: 2019-04-17 09:07:27
tags: [java基础,io/nio]
type: "categories"
categories: java NIO
---
# 一、概述
&ensp;&ensp;&ensp;&ensp;从java1.4开始提供了NIO的新特性，NIO与IO的目的相同，NIO有三个核心对象缓冲区(Buffer)、通道(chanel)、选择器(selector)
&ensp;&ensp;&ensp;&ensp;IO的方式与NIO方式的不同: I/O是以字节为单位处理数据，NIO是以代码块的方式处理数据,处理效率比按流的方式高许多。
# 二、缓冲区Buffer
缓冲区是一个可指定大小的对象，NIO的所有数据都是以缓冲区的方式处理，读写数据都是在缓冲区Buffer中进行额。而在流的I/O中，数据都是写入到Stream
![](/buffer.jpg)
&ensp;&ensp;&ensp;&ensp;一个客户端像服务端发送数据，先将数据放入缓冲区(Buffer)，然后见缓冲区的数据写入到通道(Channel)，服务端将从通道接收数据，写入缓冲区后再从缓冲区中取出。
```
import java.nio.IntBuffer;
public class TestIntBuffer {

    public static void main(String[] args) {
        // 分配新的int缓冲区，参数为缓冲区容量
        // 新缓冲区的当前位置将为零，其界限(限制位置)将为其容量。它将具有一个底层实现数组，其数组偏移量将为零。
        IntBuffer buffer = IntBuffer.allocate(8);
        for (int i = 0; i < buffer.capacity(); ++i) {
            int j = 2 * (i + 1);
            // 将给定整数写入此缓冲区的当前位置，当前位置递增
            buffer.put(j);
        }
        // 重设此缓冲区，将限制设置为当前位置，然后将当前位置设置为0
        buffer.flip();
        // 查看在当前位置和限制位置之间是否有元素
        while (buffer.hasRemaining()) {
            // 读取此缓冲区当前位置的整数，然后当前位置递增
            int j = buffer.get();
            System.out.print(j + "  ");
        }
    }
}
```
# 三、通道Channel
&ensp;&ensp;&ensp;&ensp;Channel和传统的IO的stream流功能相似，但是stream是单向操作的，InputSteam或则OutputStream。而channel是双向的。
&ensp;&ensp;&ensp;&ensp;通道Channel也是一个对象，通过它可以读取和写入数据，再Channel里面通过Buffer来存放数据，Channel读取缓冲区(Buffer)来获取这个数据。
&ensp;&ensp;&ensp;&ensp;Channel(通道)表示到实体如硬件设备、文件、网络套接字或可以执行一个或多个不同I/O操作的程序组件的开放的连接。所有的Channel都不是通过构造器创建的，而是通过传统的节点InputStream、OutputStream的getChannel方法来返回响应的Channel。Channel中最常用的三个类方法就是map、read和write，其中map方法用于将Channel对应的部分或全部数据映射成ByteBuffer，而read或write方法有一系列的重载形式，这些方法用于从Buffer中读取数据或向Buffer中写入数据。
下面是NIO的使用例子：使用NIO获取数据大致可以分为三步
(1). 从FileInputStream获取Channel 
(2). 创建Buffer 
(3). 将数据从Channel读取到Buffer中
```
//NIO读取数据
    public static void main( String args[] ) throws Exception {  
        FileInputStream fin = new FileInputStream("c:\\test.txt");  
        // 获取通道  
        FileChannel fc = fin.getChannel();  
        // 创建缓冲区  
        ByteBuffer buffer = ByteBuffer.allocate(1024);  
        // 读取数据到缓冲区  
        fc.read(buffer);  
        buffer.flip();  
        while (buffer.remaining()>0) {  
            byte b = buffer.get();  
            System.out.print(((char)b));  
        }  
        fin.close();  
    }  
//NIO写入数据
 private static final byte message[] = { 83, 111, 109, 101, 32,
        98, 121, 116, 101, 115, 46 };

    public static void main( String args[] ) throws Exception {
        FileOutputStream fout = new FileOutputStream( "c:\\test.txt" );
        
        FileChannel fc = fout.getChannel();
        
        ByteBuffer buffer = ByteBuffer.allocate( 1024 );
        
        for (int i=0; i<message.length; ++i) {
            buffer.put( message[i] );
        }
        
        buffer.flip();
        
        fc.write( buffer );
        
        fout.close();
    }
```
# 四、选择器
&ensp;&ensp;&ensp;&ensp;Selector类是NIO的核心类，Selector能够检测多个注册的通道上是否有事件发生，如果有事件发生，便获取事件然后针对每个事件进行相应的响应处理。这样一来，只是用一个单线程就可以管理多个通道，也就是管理多个连接。这样使得只有在连接真正有读写事件发生时，才会调用函数来进行读写，就大大地减少了系统开销，并且不必为每个连接都创建一个线程，不用去维护多个线程，并且避免了多线程之间的上下文切换导致的开销。
&ensp;&ensp;&ensp;&ensp;与Selector有关的一个关键类是SelectionKey，一个SelectionKey表示一个到达的事件，这2个类构成了服务端处理业务的关键逻辑。



