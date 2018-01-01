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
