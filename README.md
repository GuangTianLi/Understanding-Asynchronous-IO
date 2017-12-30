# Understanding-Asynchronous-IO
深入理解Python异步事件机制

## 前言

> "知其然，知其所以然"

* [什么是异步?][什么是异步?]
    * 同步
    * 并发(Concurrency)
        * 线程(Thread)
    * 异步(Asynchronous)
        * I/O多路复用
* [Python中的异步][Python中的异步]
    * 生成器(generator)
    * 协程(coroutines)
    * 异步(asynchronous)
         
# 什么是异步?

为了深入理解异步的概念，就必须先了解异步设计的由来。

## 同步

显然易见的是，同步的概念随着我们学习第一个输出Hello World的程序，
就已经深入人心。

然而我们也很容易忘记一个事实：一个现代编程语言(如Python)做了非常多的工作，
来指导和约束你如何去构建你自己的一个程序。

```python
def f():
    print("in f()")
def g():
    print("in g()")
f()
g()
```

你知道`in g()`一定输出在`in f()`之后，即函数f完成前函数g不会执行。这即为**同步**。
在现代编程语言的帮助下，这一切显得非常的自然，从而也让我们可以将我们的程序分解成
松散耦合的函数：一个函数并不需要关心谁调用了它，它甚至可以没有返回值，只是完成一些操作。

当然关于这些是怎么具体实现的就不探究了，然而随着一个程序的功能的增加，
同步设计的开发理念并不足以实现一些复杂的功能。

## 并发

> 写一个程序每隔3秒打印“Hello World”，同时等待用户命令行的输入。用户每输入一个自然数n，就计算并打印斐波那契函数的值F(n)，之后继续等待下一个输入

由于等待用户输入是一个阻塞的操作，如果按照同步的设计理念：如果用户未输入，
则意味着接下来的函数并不会执行，自然没有办法做到一边输出“Hello World”，一边等待用户输入。
为了让程序能解决这样一个问题，就必须引入并发机制，即让程序能够同时做很多事，线程是其中一种。

### 线程
具体代码在`example/thread_demo.py`中。

```python
from threading import Thread
from time import sleep
from time import time
from fib import timed_fib
def print_hello():
    while True:
        print("{} - Hello world!".format(int(time())))
        sleep(3)
def read_and_process_input():
    while True:
        n = int(input())
        print('fib({}) = {}'.format(n, timed_fib(n)))
def main():
    # Second thread will print the hello message. Starting as a daemon means
    # the thread will not prevent the process from exiting.
    t = Thread(target=print_hello)
    t.daemon = True
    t.start()
    # Main thread will read and process input
    read_and_process_input()
if __name__ == '__main__':
    main()
```