""" Written by Benjamin Jack Cullen """

import os
import time

x_files = []


def scantree(path: str) -> str:
    global x_files
    try:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from scantree(entry.path)
            else:
                yield entry
    except Exception as e:
        x_files.append(['[ERROR]', str(e)])


def scan_files(_path: str) -> list:
    global x_files
    x_files = []
    fp = []
    [fp.append(entry.path) for entry in scantree(_path)]
    return [fp, x_files]


def scantree_dirs(_path: str) -> str:
    global x_files
    try:
        for entry in os.scandir(_path):
            if entry.is_dir():
                yield os.path.join(_path, entry.name)
                yield from scantree_dirs(os.path.join(_path, entry.name))
    except Exception as e:
        x_files.append(['[ERROR]', str(e)])


def scan_dirs(_target: str) -> list:
    global x_files
    x_files = []
    fp = []
    [fp.append(entry) for entry in scantree_dirs(_target)]  # if os.path.isdir(entry.path)]
    return [fp, x_files]


def is_empty_dir(_path: str) -> bool:
    if os.path.exists(_path):
        if len(os.listdir(_path)) == 0:
            return True
        else:
            return False


def scan_depth_zero(path: str) -> list:
    global x_files
    path_list = os.listdir(path)
    file_list = []
    idx = 0
    for f in path_list:
        path_list[idx] = os.path.join(path, f)
        if os.path.isfile(path_list[idx]):
            file_list.append(path_list[idx])
        idx += 1
    return [file_list, []]


def pre_scan_handler(_target: str, _verbose: bool, _recursive: bool) -> tuple:
    if _recursive is True:
        scan_results = scan_files(_path=_target)
    else:
        scan_results = scan_depth_zero(path=_target)
    _files = scan_results[0]
    _x_files = scan_results[1]
    return _files, _x_files
