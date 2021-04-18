"""
easylog

Probably the most user-friendly Python logging module.

by 1MLightyears@gmail.com
on 20210329
"""
from .logger import Logger, loggers, Format, brackets
from .trigger import error_loggers

import sys

__all__ = ["default_logger", "log", "print", "error_loggers", "Logger", "brackets"]

default_logger = Logger()


def print(*args, **kwargs):
    global default_logger
    sep = kwargs.get("sep", " ")
    l = default_logger.level
    d = default_logger.dest
    default_logger.level = kwargs.get("level", l)
    default_logger.dest = kwargs.get("dest", d)
    for logger in loggers:
        # default_logger would respond in any cases,
        # other loggers would respond if their conditions met.
        logger.log(
            sep.join([str(i) for i in args]), default_logger.level, default_logger.dest
        )
    default_logger.level = l
    default_logger.dest = d


def log(*args, **kwargs):
    l = kwargs.get("level", "info")
    d = kwargs.get("dest", sys.stderr)
    sep = kwargs.get("sep", " ")
    for logger in loggers:
        logger.log(sep.join([str(i) for i in args]), l, d)
