"""
easylog

Trigger submodule.

A "trigger" is the procedure of calling logger to log. Though loggers can
trigger themselves by manually calling logger.log() in program, triggers
are those which monitor the program and call loggers when specific
conditions met.

The easylog customed exception hook(i.e. easylog_excepthook) is an exception
trigger. It aims to take place of the system default hook(sys.excepthook). It
process errors and relay them to loggers.

If needed to capture errors, Loggers should be registered to at least one
specific kind of error by Logger.register().

by 1MLightyears@gmail.com
on 20210331
"""
# standard libraries
import os
import sys
from collections import defaultdict
import re

from .parameters import Parameters

__all__ = ["original_excepthook", "error_loggers", "easylog_excepthook"]

original_excepthook = sys.excepthook

# Steps for logging exceptions by the easylog_excepthook,
# 1. define a logger
# 2. call logger.register() with the parameter of which kind of exception
#    you want it to log; default is all exceptions (BaseException)
# 3. done
# 4. use logger.unregister() to stop logging exceptions
error_loggers = defaultdict(list)  # key:error, value:list of Logger
from pprint import pprint


def easylog_excepthook(exc_type, exc_value, exc_tb):
    """
    A customed exception hook to replace default sys.excepthook.
    The original is saved in original_excepthook.
    """
    global error_loggers
    if (error_loggers[exc_type] != []) or (error_loggers[BaseException] != []):
        while exc_tb.tb_next:
            exc_tb = exc_tb.tb_next
        with open(exc_tb.tb_frame.f_code.co_filename, "r", encoding="utf-8") as f:
            for i in range(exc_tb.tb_frame.f_lineno - 1):
                f.readline()
            code = f.readline()
        d = Parameters()
        d.update(
            {
                "filefull": exc_tb.tb_frame.f_code.co_filename,
                "file": os.path.basename(exc_tb.tb_frame.f_code.co_filename),
                "lineno": exc_tb.tb_frame.f_lineno,
                "locals": list(exc_tb.tb_frame.f_locals.keys()),
                "code": code[:],
                "errtype": str(exc_type)[8:-2],
                "errvalue": str(exc_value),
                "function": exc_tb.tb_frame.f_code.co_name[:],
                "repr": [s for s in re.split(r"\b", code) if s],
            }
        )
        for i in range(len(d["repr"])):
            if (d["repr"][i] in exc_tb.tb_frame.f_locals) and (
                not callable(exc_tb.tb_frame.f_locals[d["repr"][i]])
            ):
                d["repr"][i] = str(exc_tb.tb_frame.f_locals[d["repr"][i]])
        d["repr"] = "".join(d["repr"])
        d.update(exc_tb.tb_frame.f_locals)
        for l in error_loggers[exc_type] + error_loggers[BaseException]:
            l.log(l.pattern, "error", l.dest, format_dict=d)
    else:
        original_excepthook(exc_type, exc_value, exc_tb)


sys.excepthook = easylog_excepthook
