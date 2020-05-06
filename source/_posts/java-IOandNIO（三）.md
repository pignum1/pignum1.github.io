---
title: java-IOandNIO（三）
date: 2019-04-17 12:32:34
tags: [java基础,io/nio]
type: "categories"
categories: java NIO
---
# 缓冲区Buffer解析
&ensp;&ensp;&ensp;&ensp;NIO中有两个核心对象，通道和缓冲区。缓冲区的本质是一个数组，其中添加了三个属性跟踪缓冲区的内部状态变化。其实就是STL库中Vector的设计。
**position**：指定了下一个将要被写入或者读取的元素索引，它的值由get()/put()方法自动更新，在新创建一个Buffer对象时，position被初始化为0。
**limit**：指定还有多少数据需要取出(在从缓冲区写入通道时)，或者还有多少空间可以放入数据(在从通道读入缓冲区时)。
**capacity**：指定了可以存储在缓冲区中的最大数据容量，实际上，它指定了底层数组的大小，或者至少是指定了准许我们使用的底层数组的容量。
```
    public static void main(String[] args) throws Exception{
        FileInputStream fin = new FileInputStream("c:\\test.txt");
		//获取通道连接
        FileChannel fc = fin.getChannel();
		//初始化大小为10byte的缓冲区
        ByteBuffer buffer = ByteBuffer.allocate(10);
		//通道读取缓冲区数据，此时 position =10,limit=10,capacity=10
        fc.read(buffer);
		//从缓冲区读取数据前.position =0,limit =10;
        buffer.flip();
		//get()使position递增而limit不变
        while (buffer.remaining() > 0) {
            byte b = buffer.get();
            // System.out.print(((char)b));
        }
		//将状态回复到初始的状态
        buffer.clear();
        fin.close();
    }
```
缓冲区的分配其实就是一个数组形式的数据分配，使用了allocate来指定缓冲区的容量。
缓冲区的分片，在原本的缓存区对象上切出一片来创建一个子缓冲区，但是新的缓冲区其实和原缓冲区在切出的区域上是数据共享的，勇slice方法创建一个子缓冲区。
```
ByteBuffer buffer = ByteBuffer.allocate(10);
//在缓冲区中放入0-9
for (int i=0; i<buffer.capacity(); i++) {
        buffer.put( (byte)i );
}
//在缓冲区中下标3-7的地方设置为子缓冲区
buffer.position(3);
buffer.limit(7);
ByteBuffer slice = buffer.slice();
//改编子缓冲区的内容
for (int i=0; i<slice.capacity(); i++) {
    byte b = slice.get( i );
    b *= 10;
    slice.put( i, b );
}
//自缓冲区的内容改变，原缓存区的数据也改变
//还原原缓存区的初始位置position和limit
buffer.position( 0 );
buffer.limit( buffer.capacity() );
while (buffer.remaining()>0) {
    System.out.println( buffer.get() );
}
System.out.print("\n");
```
缓存区分片同样可以创建只读缓冲区，可以通过调用缓冲区的asReadOnlyBuffer()方法，将任何常规缓冲区转 换为只读缓冲区，这个方法返回一个与原缓冲区完全相同的缓冲区，并与原缓冲区共享数据，只不过它是只读的。如果原缓冲区的内容发生了变化，只读缓冲区的内容也随之发生变化。
```
    ByteBuffer buffer = ByteBuffer.allocate( 10 );
    // 缓冲区中的数据0-9
    for (int i=0; i<buffer.capacity(); ++i) {
        buffer.put( (byte)i );
    }
    // 创建只读缓冲区
    ByteBuffer readonly = buffer.asReadOnlyBuffer();
    // 改变原缓冲区的内容
    for (int i=0; i<buffer.capacity(); ++i) {
        byte b = buffer.get( i );
        b *= 10;
        buffer.put( i, b );
    }
    readonly.position(0);
    readonly.limit(buffer.capacity());
    // 只读缓冲区的内容也随之改变
    while (readonly.remaining()>0) {
        System.out.println( readonly.get());
    }
```



