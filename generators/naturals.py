def naturals():
    yield 0
    for n in naturals():
        yield n + 1


def zeros():
    yield 0
    yield from zeros()


def repeat(x):
    yield x
    yield from repeat(x)


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


if __name__ == "__main__":
    print(list(fib(8)))
