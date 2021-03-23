# based on: https://realpython.com/python-timer/

import time

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self, start_now=False):
        self._iterations = 0
        self._start_time = time.perf_counter() if start_now else None
        self._elapsed_time = 0.0

    def __str__(self):
        return f"Iterations: {self._iterations} / Elapsed: {self._elapsed_time:0.4f} seconds / Average: {self._elapsed_time/self._iterations:0.4f} seconds"

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()
        return self

    def stop(self, show=False):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        self._elapsed_time += time.perf_counter() - self._start_time
        self._start_time = None
        self._iterations += 1
        if show: self.show()
        return self

    def show(self):
        if self._iterations == 0:
            if self._start_time is None:
                print("not started")
            else:
                print("running - no iterations completed")
        else:
            print(str(self))
        return self
