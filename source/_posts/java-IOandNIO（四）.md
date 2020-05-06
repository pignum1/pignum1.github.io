---
title: java-IOandNIO（四）
date: 2019-04-18 00:17:40
tags: [java基础,io/nio]
type: "categories"
categories: java NIO
---
# 一、通道Channel
&ensp;&ensp;&ensp;&ensp;通道既不是一个扩展也不是一项增强，而是全新的、极好的Java I/O示例，提供与I/O服务的直接连接。Channel用于在字节缓冲区和位于通道另一侧的实体（通常是一个文件或套接字）之间有效地传输数据。
&ensp;&ensp;&ensp;&ensp;通道是一种途径，缓存区是通道内部的数据发送和接收的单位。
```
public interface Channel extends Closeable {
    public boolean isOpen();
    public void close() throws IOException;
}
```
Channel接口里面有两个接口，isOpen()是判断通道是否打开，close()是关闭通道的接口
# 二、通道的基本接口
```
//只读通道接口
public interface ReadableByteChannel extends Channel {
    public int read(ByteBuffer dst) throws IOException;
}

//写入通道接口
public interface WritableByteChannel extends Channel {
	    public int write(ByteBuffer src) throws IOException;
}
//读写通道
public interface ByteChannel extends ReadableByteChannel, WritableByteChannel {
}
```
&ensp;&ensp;&ensp;&ensp;通道有阻塞和非阻塞模式，非阻塞模式的通道不会造成线程休眠，要么完成，要么返回状态。只有流的通道(如sockets、pipes)，才可以使用非阻塞的模式
下方是SocketChannel
```
public abstract class SocketChannel
    extends AbstractSelectableChannel
    implements ByteChannel, ScatteringByteChannel, GatheringByteChannel{
    ...
}
public abstract class AbstractSelectableChannel
    extends SelectableChannel
{
   ...
}
```
可以看出，socket通道类从SelectableChannel类引申而来，从SelectableChannel引申而来的类可以和支持有条件的选择的选择器（Selectors）一起使用。将非阻塞I/O和选择器组合起来可以使开发者的程序利用多路复用I/O
# 三、使用文件通道读写数据
```
public static void main(String[] args) throws Exception
{
    File file = new File("D:/files/readchannel.txt");
    FileInputStream fis = new FileInputStream(file);
    FileChannel fc = fis.getChannel();
    ByteBuffer bb = ByteBuffer.allocate(35);
    fc.read(bb);
    bb.flip();
    while (bb.hasRemaining())
    {
        System.out.print((char)bb.get());
    }
    bb.clear();
    fc.close();
}

public static void main(String[] args) throws Exception
{
    File file = new File("D:/files/writechannel.txt");
    RandomAccessFile raf = new RandomAccessFile(file, "rw");
    FileChannel fc = raf.getChannel();
    ByteBuffer bb = ByteBuffer.allocate(10);
    String str = "abcdefghij";
    bb.put(str.getBytes());
    bb.flip();
    fc.write(bb);
    bb.clear();
    fc.close();
}
```
这里使用了RandomAccessFile去获取FileChannel，然后操作其实差不多，write方法写ByteBuffer中的内容至文件中，注意写之前还是要先把ByteBuffer给flip一下。可能有人觉得这种连续put的方法非常不方便，但是没有办法，之前已经提到过了：通道只能使用ByteBuffer。
