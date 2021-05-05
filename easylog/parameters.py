"""
easylog

Parameter submodule.

Provides global parameters to be replaced in pattern string
(i.e. logger.pattern) in order to give a more detailed log.

by 1MLightyears@gmail.com
on 20210415
"""
import datetime
import os
import sys
import inspect
import getpass
import re

__all__ = ["Parameters"]


def Parameters(custom_para: dict = {}):
    for user_file in inspect.stack():
        parent = user_file.filename.split(os.sep)[-2]
        if parent != "easylog":
            break
    d = {
        "date": datetime.date.today(),
        "time": str(datetime.datetime.now()).split()[-1],
        "pwd": os.getcwd(),
        "filefull": user_file.filename,
        "file": os.path.basename(user_file.filename),
        "lineno": user_file.lineno,
        "code": user_file.code_context[0],
        "repr": [s for s in re.split(r"\b", user_file.code_context[0]) if s],
        "function": user_file.function,
        "user": getpass.getuser(),
    }
    for i in range(len(d["repr"])):
        if (d["repr"][i] in user_file.frame.f_locals) and (not callable(
                user_file.frame.f_locals[d["repr"][i]])):
            d["repr"][i] = str(user_file.frame.f_locals[d["repr"][i]])
    d["repr"] = "".join(d["repr"])
    d.update(custom_para)
    return d
