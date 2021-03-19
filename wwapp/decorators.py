import time
import functools


""" PROFILING DECORATORS """


def time_task(func):
    """Prints time taken to complete a task in milliseconds"""
    @functools.wraps(func)
    def timed_func(request, *args, **kwargs):
        t1 = time.time()
        result = func(request, *args, **kwargs)
        # print(f"Time taken to {func.__name__!r}: {(time.time() - t1) * float(1000000)}usec")
        print(f"Time taken to {func.__name__!r}: {(time.time() - t1) * float(1000)}ms")
        return result

    return timed_func
