"""
easylog

Logger submodule.

In easylog, a "logger" is a kind of objects that writes log messages into
log files. Usually they are called by "triggers".

by 1MLightyears@gmail.com
on 20210329
"""

import sys
import re

from .trigger import error_loggers, Parameters

__all__ = ["resolve", "loggers", "brackets", "Logger"]

# limit which methods should be resolved by a logger
resolve = ["info", "warning", "error", "fatal", "critical", "debug", "failure"]
loggers = []
brackets = r"<>"


def Format(log_msg: str = "", format_dict: dict = {}):
    """
    translates log strings to plain strings and add "\n".

    log_msg(str):the log message.
    format_dict(defaultdict(str)):a mapping dict, describes the real values of
         the "%***%"-like substrings. the default "bracket" is "%***%" and can
         be changed by setting easylog.logger.brackets.
    """
    # see if brackets is legal
    global brackets
    if len(brackets) != 2 or not isinstance(brackets, str):
        brackets = r"<>"
    sub_list = list(
        set(re.findall(brackets[0] + r"([a-zA-Z0-9_]+)" + brackets[1],
                       log_msg)))
    for format_str in sub_list:
        val = "N/A"
        if format_str in format_dict:
            val = str(format_dict[format_str])
        log_msg = log_msg.replace(brackets[0] + format_str + brackets[1], val)
    return log_msg


class Logger:
    """
    A logger is the module that respond to logging requests.
    Logging requests could be triggered by manually calling easylog.log, or by
    easylog.Monitor catching exceptions(if exists and is enabled).
    A logger will answer to a logging requests when it has the resolve method
    the request needs. Then it writes the message to stdout/a specific file.
    """
    def __init__(
        self,
        level: str = "info",
        dest=sys.stdout,
        exc_type=None,
        pattern: str = brackets[0] + r"log" + brackets[1],
    ):
        """
        Create a logger.

        Parameter:
        ------
        level(str): the logger only records a log message if they have the
            same level.
        dest(io.IOWrapper): the destination of the log message to be written,
            can be a file or stderr(default) or any indicator that implemented
            "write()" method.
            parsed by this logger.
        pattern(str): format of log message.
        """
        global loggers
        self.enabled = True  # enabled(bool): whether the logger is activated.
        self.level = level
        self.dest = dest
        self.register(exc_type)
        loggers.append(self)
        self.pattern = pattern

    def log(
        self,
        log_msg: str = "",
        log_level: str = "info",
        log_dest=sys.stdout,
        format_dict: dict = {},
    ):
        """
        The actual logging method.
        The logger checks if the log message meets its logging standard and
        write it to self.dest if so.

        Parameters
        ------
        log_msg(str):the log message.
        log_level(str):level of the log message.
        log_dest(io.IOWrapper):destination of the log message.
        format_dict(defaultdict(str)):a mapping dict used by Format.
        """
        if not self.enabled:
            return -1
        format_dict.update({
            "log": log_msg,
            "level": self.level,
            "dest": self.dest
        })
        d = Parameters()
        d.update(format_dict)
        if log_level.lower() == self.level:
            if log_dest == self.dest:
                close_later = False
                if isinstance(self.dest, str):
                    close_later = True
                    self.dest = open(self.dest, "a+", encoding="utf-8")
                elif not self.dest.writable():
                    close_later = True
                    self.dest = open(self.dest.name, "a+", encoding="utf-8")
                self.dest.write(Format(self.pattern, d) + "\n")
                if close_later:
                    self.dest.close()
                return 0
        return -1

    def close(self):
        """
        Remove the logger from logger list so that it'll no longer accept new
        log message.
        """
        global loggers
        loggers.remove(self)

    def register(self, exc_type=BaseException):
        """
        Register this logger in monitor.error_loggers, so that when an
        'exc_type' exception happens, this logger would log it.

        Parameter
        ------
        exc_type(subclass of BaseException):Certain exception. Directly exit
            if None.
        """
        self.exc_type = exc_type
        if exc_type:
            error_loggers[exc_type].append(self)
        else:
            self.unregister()

    def unregister(self):
        """
        Unregister this logger in monitor.error_loggers.
        """
        if self in error_loggers:
            error_loggers[self.exc_type].remove(self)
        self.exc_type = None
