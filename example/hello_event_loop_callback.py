import selectors
import sys
from bisect import insort
from time import time

from fib import timed_fib


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
