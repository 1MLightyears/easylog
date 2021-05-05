"""
easylog

Probably the most user-friendly Python logging module.

by 1MLightyears@gmail.com
on 20210329
"""
from .logger import Logger, loggers, Format, brackets
from .trigger import error_loggers

import sys
from functools import partial

__all__ = [
    "default_logger", "log", "print", "error_loggers", "Logger", "brackets",
    "info", "warning", "error", "fatal", "debug"
]

default_logger = Logger()


def log(*args, sep=" ", level="info", dest=sys.stderr):
    """
    Write the log message.
    In fact, this function broadcast a log request to all loggers, see if any
    logger answer the request.
    """
    for logger in loggers:
        logger.log(sep.join([str(i) for i in args]), level, dest)


def print(*args, **kwargs):
    """
    'print' the log message to designated dest and level for once.
    The default logger(i.e. default_logger) will always answer, while
    other loggers answer when their dest & level match the designated dest &
    level.
    """
    global default_logger
    sep = kwargs.get("sep", " ")
    l = default_logger.level
    d = default_logger.dest
    default_logger.level = kwargs.get("level", "info")
    default_logger.dest = kwargs.get("dest", sys.stderr)

    # default_logger would respond in any cases,
    # other loggers would respond if their conditions met.
    log(*args, sep=sep, level=default_logger.level, dest=default_logger.dest)

    default_logger.level = l
    default_logger.dest = d


# for legacy use

info = partial(log, level="info")
warning = partial(log, level="warning")
error = partial(log, level="error")
fatal = partial(log, level="fatal")
debug = partial(log, level="debug")
