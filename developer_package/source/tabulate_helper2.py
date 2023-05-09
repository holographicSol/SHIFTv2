""" Written by Benjamin Jack Cullen """

import os
import subprocess
import screeninfo
import shutil
import textwrap


def chunk_data(data, chunk_size: int) -> list:
    _chunks = [data[x:x + chunk_size] for x in range(0, len(data), chunk_size)]
    data = []
    for _chunk in _chunks:
        data.append(_chunk)
    return data


def longest_item(_list: list, idx: int) -> int:
    i_longest = 0
    for item in _list:
        try:
            if len(str(item[idx])) >= i_longest:
                i_longest = len(str(item[idx]))
        except Exception as e:
            print(item, e)
            pass
    return i_longest


def column_width_from_screen_size_using_ratio(n: int, reduce=0, add=0, ratio=0.134) -> int:
    """ Default ratio defined for font size 12 at screen width 1920. """
    w = 64
    for m in screeninfo.get_monitors():
        if m.is_primary is True:
            w = m.width
    return add_sub(n=int(int(w * ratio) / set_n(n)), reduce=reduce, add=add)


def column_width_from_os_get_terminal_size(n: int, reduce=0, add=0) -> int:
    return add_sub(n=int(int(os.get_terminal_size().columns) / set_n(n)), reduce=reduce, add=add)


def column_width_from_tput(n: int, reduce=0, add=0) -> int:
    w = int(int(int(subprocess.Popen(['tput', 'cols'], stdout=subprocess.PIPE).communicate()[0].strip())) / set_n(n))
    return add_sub(n=w, reduce=reduce, add=add)


def column_width_from_shutil(n: int, reduce=0, add=0):
    w = int(int(shutil.get_terminal_size().columns) / int(set_n(n)))
    return add_sub(n=w, reduce=reduce, add=add)


def add_sub(n, reduce=0, add=0):
    n -= reduce
    n += add
    return n


def set_n(n):
    if n <= 0:
        n = 1
    return n


def add_padding_and_new_lines_to_columns(data: list, col_idx: int, max_column_width=None, padding_left=True) -> list:
    """ Accepts data as a list of lists [ [1,2,3], [1,2,3] ] """

    _results = data

    # max_column_width is not set so set max_column_width using col_idx
    if max_column_width is None:
        max_column_width = 0
        for r in _results:
            if len(str(r[col_idx])) > max_column_width:
                max_column_width = len(str(r[col_idx]))

    # add padding and newlines for specified col_idx
    n_result = 0
    for r in _results:
        # isolate item length
        len_r = len(str(r[col_idx]))
        if len_r < max_column_width:
            # add padding
            if padding_left is True:
                _results[n_result][col_idx] = str(' ' * int(max_column_width - len_r)) + str(r[col_idx])
            else:
                _results[n_result][col_idx] = str(r[col_idx]) + str(' ' * int(max_column_width - len_r))
        else:
            # break into chunks of max_column_width and add new lines
            tmp = textwrap.wrap(str(r[col_idx]), max_column_width, replace_whitespace=False)
            new_item = tmp[0]
            n_tmp = 0
            for x in tmp:
                if n_tmp != 0:
                    new_item = new_item + '\n' + x
                n_tmp += 1
            # put back into the sub list
            _results[n_result][col_idx] = new_item
        n_result += 1

    # return the formatted data
    return _results
