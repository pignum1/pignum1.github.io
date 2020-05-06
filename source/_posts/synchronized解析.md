---
title: synchronized解析
date: 2019-04-26 12:57:37
tags: [多线程,synchronized]
type: "categories"
categories: java线程
---
//todo 
# synchronized的底层实现原理
Java 虚拟机中的同步(Synchronization)基于进入和退出管程(Monitor)对象实现， 无论是显式同步(有明确的 monitorenter 和 monitorexit 指令,即同步代码块)还是隐式同步都是如此。在 Java 语言中，同步用的最多的地方可能是被 synchronized 修饰的同步方法。
