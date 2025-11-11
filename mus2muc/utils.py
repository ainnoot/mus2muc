import sys
from time import perf_counter


class Logger:
    start = perf_counter()
    LOG_LINE = "[{timestamp:.3f}] {message}"

    @staticmethod
    def log(message):
        timestamp = perf_counter() - Logger.start
        print(
            Logger.LOG_LINE.format(timestamp=timestamp, message=message),
            file=sys.stderr,
        )


def log(message):
    Logger.log(message)
