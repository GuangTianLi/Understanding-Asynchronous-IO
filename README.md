# Understanding-Asynchronous-IO
深入理解Python异步事件机制

## 前言

> "知其然，知其所以然"

* [什么是异步](#什么是异步)
    * 同步
    * 并发(Concurrency)
        * 线程(Thread)
        * I/O多路复用
    * 异步(Asynchronous)
        * 回调(Callback)
        * 协程(Coroutines)
              
* [Python中的异步](#Python中的异步)
    * 生成器(generator)
    * 协程(coroutines)
    * 异步(asynchronous)
* [参考文献](#参考文献)
         
# 什么是异步

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
具体代码在`example/hello_threads.py`中。

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

对于之前那样的问题，引入线程机制就可以解决这种简单的并发问题。而对于线程我们应该有一个简单的认知：

* 一个线程可以理解为指令的序列和CPU执行的上下文的集合。
* 一个同步的程序即进程，有且只会在一个线程中运行，所以当线程被阻塞，也就意味着整个进程被阻塞
* 一个进程可以有多个线程，同一个进程中的线程共享了进程的一些资源，比如说内存，地址空间，文件描述符等。
* 线程是由**操作系统的调度器**来调度的， 调度器统一负责管理调度进程中的线程。
    * 系统的调度器决定什么时候会把当前线程挂起，并把CPU的控制器交个另一个线程。这个过程称之为称**上下文切换**，包括对于当前线程上下文的保存、对目标线程上下文的加载。
    * 上下文切换会对性能产生影响，因为它本身也需要CPU的周期来执行

### I/O多路复用

而随着现实问题的复杂化，如10K问题。

> 在Nginx没有流行起来的时候，常被提到一个词 10K（并发1W）。在互联网的早期，网速很慢、用户群很小需求也只是简单的页面浏览，所以最初的服务器设计者们使用基于进程/线程模型，也就是一个TCP连接就是分配一个进程(线程)。谁都没有想到现在Web 2.0时候用户群里和复杂的页面交互问题，而现在即时通信和实在实时互动已经很普遍了。那么你设想如果每一个用户都和服务器保持一个（甚至多个）TCP连接才能进行实时的数据交互，别说BAT这种量级的网站，就是豆瓣这种比较小的网站，同时的并发连接也要过亿了。进程是操作系统最昂贵的资源，一台机器无法创建很多进程。如果要创建10K个进程，那么操作系统是无法承受的。就算我们不讨论随着服务器规模大幅上升带来复杂度几何级数上升的问题，采用分布式系统，只是维持1亿用户在线需要10万台服务器，成本巨大，也只有FLAG、BAT这样公司才有财力购买如此多的服务器。

而同样存在一些原因，让我们避免考虑多线程的方式：

* 线程在计算和资源消耗的角度来说是比较昂贵的。
* 线程并发所带来的问题，比如因为共享的内存空间而带来的死锁和竞态条件。这些又会导致更加复杂的代码，在编写代码的时候需要时不时地注意一些线程安全的问题。

为了解决这一问题，出现了「用同一进程/线程来同时处理若干连接」的思路，也就是I/O多路复用。

以Linux操作系统为例，Linux操作系统给出了三种监听文件描述符的机制，具体实现可[参考](http://www.cnblogs.com/Anker/p/3265058.html)：

* select: 每个连接对应一个描述符（socket），循环处理各个连接，先查下它的状态，ready了就进行处理，不ready就不进行处理。但是缺点很多：
    * 每次调用select，都需要把fd集合从用户态拷贝到内核态，这个开销在fd很多时会很大
    * 同时每次调用select都需要在内核遍历传递进来的所有fd，这个开销在fd很多时也很大
    * select支持的文件描述符数量太小了，默认是1024
* poll: 本质上和select没有区别，但是由于它是基于链表来存储的，没有最大连接数的限制。缺点是：
    * 大量的的数组被整体复制于用户态和内核地址空间之间，而不管这样的复制是不是有意义。
    * poll的特点是「水平触发(只要有数据可以读，不管怎样都会通知)」，如果报告后没有被处理，那么下次poll时会再次报告它。
* epoll: 它使用一个文件描述符管理多个描述符，将用户关系的文件描述符的事件存放到内核的一个事件表中，这样在用户空间和内核空间的copy只需一次。epoll支持水平触发和边缘触发，最大的特点在于「边缘触发」，它只告诉进程哪些刚刚变为就绪态，并且只会通知一次。使用epoll的优点很多：
    * 没有最大并发连接的限制，能打开的fd的上限远大于1024（1G的内存上能监听约10万个端口）
    * 效率提升，不是轮询的方式，不会随着fd数目的增加效率下降
    * 内存拷贝，利用mmap()文件映射内存加速与内核空间的消息传递；即epoll使用mmap减少复制开销
    
综上所述，通过epoll的机制，给现代高级语言提供了高并发、高性能解决方案的基础。而同样FreeBSD推出了kqueue，Windows推出了IOCP，Solaris推出了/dev/poll。

而在Python3.4中新增了[selectors模块](https://docs.python.org/3/library/selectors.html)，用于封装各个操作系统所提供的I/O多路复用的接口。
那么之前同样的问题，我们可以通过I/O多路复用的机制实现并发。

> 写一个程序每隔3秒打印“Hello World”，同时等待用户命令行的输入。用户每输入一个自然数n，就计算并打印斐波那契函数的值F(n)，之后继续等待下一个输入

通过最基础的轮询机制(poll)，轮询标准输入(stdin)是否变为可读的状态，从而当标准输入能被读取时，去执行计算Fibonacci数列。然后判断时间是否过去三秒钟，从而是否输出"Hello World!".
具体代码在`example/hello_selectors_poll.py`中。

**注意**：在Windows中并非一切都是文件描述符，所以该实例代码无法在Windows平台下运行。

```python
import selectors
import sys
from time import time
from fib import timed_fib
def process_input(stream):
    text = stream.readline()
    n = int(text.strip())
    print('fib({}) = {}'.format(n, timed_fib(n)))
def print_hello():
    print("{} - Hello world!".format(int(time())))
def main():
    selector = selectors.DefaultSelector()
    # Register the selector to poll for "read" readiness on stdin
    selector.register(sys.stdin, selectors.EVENT_READ)
    last_hello = 0  # Setting to 0 means the timer will start right away
    while True:
        # Wait at most 100 milliseconds for input to be available
        for event, mask in selector.select(0.1):
            process_input(event.fileobj)
        if time() - last_hello > 3:
            last_hello = time()
            print_hello()
if __name__ == '__main__':
    main()
```

从上面解决问题的设计方案演化过程，从同步到并发，从线程到I/O多路复用。可以看出根本思路去需要程序本身高效去阻塞，
让CPU能够执行核心任务。意味着将数据包处理，内存管理，处理器调度等任务从内核态切换到应用态，操作系统只处理控制层，
数据层完全交给应用程序在应用态中处理。极大程度的减少了程序在应用态和内核态之间切换的开销，让高性能、高并发成为了可能。


## 异步

通过之前的探究，不难发现一个同步的程序也能通过操作系统的接口实现“并发”，而这种“并发”的行为即可称之为**异步**。

之前通过I/O复用的所提供的解决方案，进一步抽象，即可抽象出最基本的框架**事件循环(Event Loop)**，而其中最容易理解的实现，
则是**回调(Callback)**.

### 回调

通过对事件本身的抽象，以及其对应的处理函数(handler)，可以利用实现如下算法：

> 维护一个按时间排序的事件列表，最近需要运行的定时器在最前面。这样的话每次只需要从头检查是否有超时的事件并执行它们。
https://docs.python.org/3/library/bisect.html

[bisect.insort](https://docs.python.org/3/library/bisect.html)使得维护这个列表更加容易，它会帮你在合适的位置插入新的定时器事件组。
具体代码在`example/hello_event_loop_callback.py`中。

**注意**：在Windows中并非一切都是文件描述符，所以该实例代码无法在Windows平台下运行。
```python
from bisect import insort
from fib import timed_fib
from time import time
import selectors
import sys
class EventLoop(object):
    """
    Implements a callback based single-threaded event loop as a simple
    demonstration.
    """
    def __init__(self, *tasks):
        self._running = False
        self._stdin_handlers = []
        self._timers = []
        self._selector = selectors.DefaultSelector()
        self._selector.register(sys.stdin, selectors.EVENT_READ)
    def run_forever(self):
        self._running = True
        while self._running:
            # First check for available IO input
            for key, mask in self._selector.select(0):
                line = key.fileobj.readline().strip()
                for callback in self._stdin_handlers:
                    callback(line)
            # Handle timer events
            while self._timers and self._timers[0][0] < time():
                handler = self._timers[0][1]
                del self._timers[0]
                handler()
    def add_stdin_handler(self, callback):
        self._stdin_handlers.append(callback)
    def add_timer(self, wait_time, callback):
        insort(self._timers, (time() + wait_time, callback))
    def stop(self):
        self._running = False
def main():
    loop = EventLoop()
    def on_stdin_input(line):
        if line == 'exit':
            loop.stop()
            return
        n = int(line)
        print("fib({}) = {}".format(n, timed_fib(n)))
    def print_hello():
        print("{} - Hello world!".format(int(time())))
        loop.add_timer(3, print_hello)
    def f(x):
        def g():
            print(x)
        return g
    loop.add_stdin_handler(on_stdin_input)
    loop.add_timer(0, print_hello)
    loop.run_forever()
if __name__ == '__main__':
    main()
```

# 参考文献

* [Some thoughts on asynchronous API design in a post-async/await world](https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/)
* [Python 开源异步并发框架的未来](https://segmentfault.com/a/1190000000471602)
* [Understanding Asyncio Node.js Python3.4](http://sahandsaba.com/understanding-asyncio-node-js-python-3-4.html)
* [使用Python进行并发编程-asyncio篇(一)](http://www.dongwm.com/archives/%E4%BD%BF%E7%94%A8Python%E8%BF%9B%E8%A1%8C%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B-asyncio%E7%AF%87/)
* [select、poll、epoll之间的区别总结`[整理]`](http://www.cnblogs.com/Anker/p/3265058.html)


