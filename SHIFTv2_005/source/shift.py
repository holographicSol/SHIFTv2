""" Written by Benjamin Jack Cullen

SHIFT v2: copy, update, mirror. (File backup software)

1: scandir source, scandir destination, scandir destination directories (3x async multiprocess).
2. stat source, destination files for modified times, sizes. (2x(+pool) async multiprocess). -> Check types in lists and len().
3. enumerate tasks: copy new, update existing, delete. (3x(+pool) async multiprocess). -> Check types in lists and len().
4. run tasks: copy new, update existing, delete. (async only).
5. finally if mirror then delete directories not exist in source. (synchronous).

# todo -> testing (account for things you probably shouldn't do yet that you probably can actually do (but shouldn't)):
    * test different kinds of paths (for example network paths).


See shift -h for help.

"""

import asyncio
import aiofiles
import aiofiles.os
import aiomultiprocess
from aiomultiprocess import Worker
import cprint
import dataclasses
from dataclasses import dataclass
import datetime
import multiprocessing
import os
import scanfs
from send2trash import send2trash
import shift_help
import sys
import time
import tabulate_helper2
import shutil
import unicodedata

# set color for time, tag, data
c_debug = 'Y'
c_time = 'BL'
c_tag = 'BL'
c_data = 'BL'


@dataclass(slots=True)
class ShiftDataClass:
    debug: bool
    verbose: bool
    no_input: bool
    mode: int
    source: str
    destination: str
    no_bin: bool


_dataclass = dataclasses.dataclass


def get_dt() -> str:
    """ formatted datetime string for tagging output """
    return str(cprint.color(s='[' + str(datetime.datetime.now()) + ']', c=c_time))


def convert_timestamp_to_datetime(timestamp: str) -> str:
    dt = str(datetime.datetime.fromtimestamp(timestamp))
    dt = dt.replace('-', ' ')
    dt = dt.split(' ')
    dt = dt[2] + '/' + dt[1] + '/' + dt[0] + '    ' + dt[3]
    if '.' in dt:
        dt = dt.split('.')
        dt = dt[0]
    return dt


def NFD(text):
    return unicodedata.normalize('NFD', text)


def canonical_caseless(text):
    return NFD(NFD(text).casefold())


def convert_bytes(num: int) -> str:
    """ bytes for humans """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def out_of_disk_space(_path: str, _size: int) -> bool:
    total, used, free = shutil.disk_usage(_path)
    if free > _size + 1:
        return False
    else:
        return True


def free_disk_space(_path: str) -> bool:
    total, used, free = shutil.disk_usage(_path)
    return free


def remove_file(_file: str):
    send2trash(_file)


def _remove_dirs(_path: str, _dataclass: dataclasses.dataclass):
    # This function is synchronous because it can delete trees
    # get the directory the file was deleted in
    _idx_current_dir = _path.rfind('\\')
    # create inverted hypo path: hypothetical path created from source directory and destination file
    hypo_path = _path[len(_dataclass.destination):]
    hypo_path = _dataclass.source + hypo_path
    # test inverted hypo path exists
    if not os.path.exists(hypo_path):
        try:
            if os.path.exists(_path):
                if _dataclass.verbose is True:
                    print(f'{get_dt()} {cprint.color(s="[DELETING] [DIRECTORY]", c="Y")} {cprint.color(s=_path, c=c_data)}')
                shutil.rmtree(_path, ignore_errors=False)
        except FileNotFoundError as e:
            print(f'{get_dt()} [FileNotFoundError] [DELETE DIR] {_path} {str(e)}')
            # _data.append(f'[FileNotFoundError] [DELETE DIR] {str(e)}')
        except PermissionError as e:
            print(f'{get_dt()} [PermissionError] [DELETE DIR] {_path} {str(e)}')
            # _data.append(f'[PermissionError] [DELETE DIR] {str(e)}')
        except OSError as e:
            print(f'{get_dt()} [OSError] [DELETE DIR] {_path} {str(e)}')
            # _data.append(f'[OSError] [DELETE DIR] {str(e)}')


async def async_remove_file(_data: list, _dataclass: dataclasses.dataclass) -> list:
    if _dataclass.verbose is True:
        print(f'{get_dt()} {cprint.color(s="[DELETING] [FILE]", c="Y")} {cprint.color(s=_data[0], c=c_data)}')
    try:
        # move to trash
        if _dataclass.no_bin is False:
            await asyncio.to_thread(remove_file, _file=_data[0])
        # os remove
        elif _dataclass.no_bin is True:
            os.remove(_data[0])
        _data.append(True)

    except FileNotFoundError as e:
        print(f'{get_dt()} [FileNotFoundError] [DELETE FILE] {_data} {str(e)}')
        _data.append(f'[FileNotFoundError] [DELETE FILE] {str(e)}')
    except PermissionError as e:
        print(f'{get_dt()} [PermissionError] [DELETE FILE] {_data} {str(e)}')
        _data.append(f'[PermissionError] [DELETE FILE] {str(e)}')
    except OSError as e:
        print(f'{get_dt()} [OSError] [DELETE FILE] {_data} {str(e)}')
        _data.append(f'[OSError] [DELETE FILE] {str(e)}')

    return _data


async def async_write(_data: list, _dataclass: dataclasses.dataclass()) -> list:
    if _dataclass.verbose is True:
        if _data[4] == '[COPYING]':
            print(f'{get_dt()} {cprint.color(s=_data[4], c="G")} {cprint.color(s=f"{_data[0]} [->] {_data[3]}", c=c_data)}')
        elif _data[4] == '[UPDATING]':
            print(f'{get_dt()} {cprint.color(s=_data[4], c="B")} {cprint.color(s=f"{_data[0]} [->] {_data[3]}", c=c_data)}')
    # create directory tree
    idx_variable_tree = _data[3].rfind('\\')
    variable_tree = _data[3][:idx_variable_tree]
    try:
        # make directories if needed
        await aiofiles.os.makedirs(variable_tree, exist_ok=True)
        if await aiofiles.os.path.exists(variable_tree):

            # Windows
            if sys.platform.startswith('win'):
                await asyncio.to_thread(shutil.copyfile, _data[0], _data[3])

            # Linux:
            elif sys.platform.startswith('linux'):
                await aiofiles.os.sendfile(_data[3], _data[0], 0, _data[2])

            # check if destination file exists
            if await aiofiles.os.path.exists(_data[3]):
                # get bytes of destination file
                stat_file = await aiofiles.os.stat(_data[3])
                sz_dst = stat_file.st_size
                # compare source file bytes to destination file bytes
                if sz_dst == _data[2]:
                    _data.append(True)
    except FileNotFoundError as e:
        print(f'{get_dt()} [FileNotFoundError] {_data} {str(e)}')
        _data.append(str(e))
    except PermissionError as e:
        print(f'{get_dt()} [PermissionError] {_data} {str(e)}')
        _data.append(str(e))
    return _data


async def scan_check(_file: str) -> list:
    try:
        stat_file = await aiofiles.os.stat(_file)
        mtime = stat_file.st_mtime
        sz = stat_file.st_size
        return [_file, mtime, sz]
    except FileNotFoundError as e:
        print(f'{get_dt()} [FileNotFoundError] {_file} {str(e)}')
    except PermissionError as e:
        print(f'{get_dt()} [PermissionError] {_file} {str(e)}')


async def get_copy_tasks(sublist: list, dir_src: str, dir_dst: str) -> list:
    # create hypo path: hypothetical path created from destination directory and source file
    hypo_path = sublist[0]
    hypo_path = hypo_path[len(dir_src):]
    hypo_path = dir_dst + hypo_path
    sublist.append(hypo_path)
    # test hypo path exists
    if not await aiofiles.os.path.exists(hypo_path):
        # hypo path exists: allow one instance of hypo path in sublist
        if hypo_path not in sublist:
            sublist.append(hypo_path)
        # hypo path exists: allow one instance of task in sublist
        if '[COPYING]' not in sublist:
            sublist.append('[COPYING]')
            return sublist


async def get_update_tasks(sublist: list, dir_src: str, dir_dst: str) -> list:
    # create hypo path: hypothetical path created from destination directory and source file
    hypo_path = sublist[0]
    hypo_path = hypo_path[len(dir_src):]
    hypo_path = dir_dst + hypo_path
    # test hypo path exists
    if await aiofiles.os.path.exists(hypo_path):
        # hypo path exists: stat hypo path
        stat_file = await aiofiles.os.stat(hypo_path)
        mtime = stat_file.st_mtime
        # hypo path exists: check if source file modified time is greater than destination file modified time
        if float(sublist[1]) > float(mtime):
            # hypo path exists: allow one instance of hypo path in sublist
            if hypo_path not in sublist:
                sublist.append(hypo_path)
            # hypo path exists: allow one instance of task in sublist
            if '[UPDATING]' not in sublist:
                sublist.append('[UPDATING]')
                return sublist


async def get_delete_tasks(sublist: list, dir_src: str, dir_dst: str) -> list:
    # create inverted hypo path: hypothetical path created from source directory and destination file
    hypo_path = sublist[0]
    hypo_path = hypo_path[len(dir_dst):]
    hypo_path = dir_src + hypo_path
    # test inverted hypo path exists
    if not await aiofiles.os.path.exists(hypo_path):
        # inverted hypo path exists: allow one instance of hypo path in sublist
        if hypo_path not in sublist:
            sublist.append(hypo_path)
        # inverted hypo path exists: allow one instance of task in sublist
        if '[DELETING]' not in sublist:
            sublist.append('[DELETING]')
            return sublist


async def scan_source(**kwargs) -> list:
    # scandir source
    dir_src = kwargs.get('dir_src')
    print(f'{get_dt()} {cprint.color(s=f"[SCANNING] [FILES]", c=c_tag)} {cprint.color(s=dir_src, c=c_data)}')
    return list(scanfs.pre_scan_handler(_target=dir_src, _verbose=False, _recursive=True))


async def scan_destination(**kwargs) -> list:
    # scandir destination
    dir_dst = kwargs.get('dir_dst')
    print(f'{get_dt()} {cprint.color(s=f"[SCANNING] [FILES]", c=c_tag)} {cprint.color(s=dir_dst, c=c_data)}')
    return list(scanfs.pre_scan_handler(_target=dir_dst, _verbose=False, _recursive=True))


async def scan_destination_directories(**kwargs) -> list:
    # scandir directories in destination
    dir_dst = kwargs.get('dir_dst')
    print(f'{get_dt()} {cprint.color(s=f"[SCANNING] [DIRECTORIES]", c=c_tag)} {cprint.color(s=dir_dst, c=c_data)}')
    return list(scanfs.scan_dirs(_target=dir_dst))


async def main_worker_stat_results(_chunks: list):
    # stat files: create aiomultiprocess pool for chunks of files
    async with aiomultiprocess.Pool() as pool:
        _results = await pool.map(entry_point_worker_stat_results, _chunks, {})
        return _results


async def entry_point_worker_stat_results(_files_src: list) -> list:
    # stat files: get modified time and size for files in chunk
    tasks = []
    [tasks.append(asyncio.create_task(scan_check(_file=file))) for file in _files_src]
    return await asyncio.gather(*tasks)


async def main_enum_copy_tasks(_chunks: list, _multiproc_dict: dict) -> list:
    # enum copy tasks: create aiomultiprocess pool for chunks of files
    async with aiomultiprocess.Pool() as pool:
        _results = await pool.map(entry_point_worker_enum_copy_tasks, _chunks, _multiproc_dict)
        return _results


async def entry_point_worker_enum_copy_tasks(stat_results_src: list, **kwargs) -> list:
    # enum copy tasks: return files to be copied
    dir_src = kwargs.get('dir_src')
    dir_dst = kwargs.get('dir_dst')
    tasks = []
    [tasks.append(asyncio.create_task(get_copy_tasks(sublist, dir_src, dir_dst))) for sublist in stat_results_src]
    _copy_tasks = await asyncio.gather(*tasks)
    _copy_tasks[:] = [sublist for sublist in _copy_tasks if sublist is not None]
    return _copy_tasks


async def main_enum_update_tasks(_chunks: list, _multiproc_dict: dict) -> list:
    # enum update tasks: create aiomultiprocess pool for chunks of files
    async with aiomultiprocess.Pool() as pool:
        _results = await pool.map(entry_point_worker_enum_update_tasks, _chunks, _multiproc_dict)
        return _results


async def entry_point_worker_enum_update_tasks(stat_results_src: list, **kwargs) -> list:
    # enum update tasks: return files to be updated
    dir_src = kwargs.get('dir_src')
    dir_dst = kwargs.get('dir_dst')
    tasks = []
    [tasks.append(asyncio.create_task(get_update_tasks(sublist, dir_src, dir_dst))) for sublist in stat_results_src]
    _update_tasks = await asyncio.gather(*tasks)
    _update_tasks[:] = [sublist for sublist in _update_tasks if sublist is not None]
    return _update_tasks


async def main_enum_delete_tasks(_chunks: list, _multiproc_dict: dict) -> list:
    # enum delete tasks: create aiomultiprocess pool for chunks of files
    async with aiomultiprocess.Pool() as pool:
        _results = await pool.map(entry_point_worker_enum_delete_tasks, _chunks, _multiproc_dict)
        return _results


async def entry_point_worker_enum_delete_tasks(stat_results_dst: list, **kwargs) -> list:
    # enum delete tasks: return files to be deleted
    dir_src = kwargs.get('dir_src')
    dir_dst = kwargs.get('dir_dst')
    tasks = []
    [tasks.append(asyncio.create_task(get_delete_tasks(sublist, dir_src, dir_dst))) for sublist in stat_results_dst]
    _delete_tasks = await asyncio.gather(*tasks)
    _delete_tasks[:] = [sublist for sublist in _delete_tasks if sublist is not None]
    return _delete_tasks


async def user_accept(_dataclass: dataclasses.dataclass):
    accept = False
    if _dataclass.no_input is False:
        user_input = input(f'{get_dt()} {cprint.color(s=f"[CONTINUE?] (Y/N): ", c="BL")}')
        if canonical_caseless(user_input) == canonical_caseless('Y'):
            accept = True
        elif canonical_caseless(user_input) == canonical_caseless('N'):
            accept = False
        else:
            print(f'{get_dt()} {cprint.color(s=f"[INVALID INPUT]", c=c_tag)} {cprint.color(s="", c=c_data)}')
            await user_accept(_dataclass)
    elif _dataclass.no_input is True:
        accept = True
    return accept


async def main(_dataclass: dataclasses.dataclass):
    print('')
    print('')
    print(f'[          SHIFTv2         ]')
    print('')
    # variably display selected mode
    _modes_list = ['[COPY MISSING]', '[UPDATE]', '[MIRROR]']
    _mode = _dataclass.mode
    print(f'{get_dt()} {_modes_list[_mode]}')

    # display specified source, destination (-s, -d)
    dir_src = _dataclass.source
    dir_dst = _dataclass.destination
    print(f'{get_dt()} {cprint.color(s=f"[SOURCE]", c=c_tag)} {cprint.color(s=dir_src, c=c_data)}')
    print(f'{get_dt()} {cprint.color(s=f"[DESTINATION]", c=c_tag)} {cprint.color(s=dir_dst, c=c_data)}')

    # scandir source and destination (3x async multi-processes)
    print(f'{get_dt()} {cprint.color(s=f"[RUNNING] [SCAN]", c=c_tag)}')
    t_scandir = time.perf_counter()
    worker_scan_source = Worker(
        target=scan_source,
        kwargs={'dir_src': dir_src}
    )
    worker_scan_destination = Worker(
        target=scan_destination,
        kwargs={'dir_dst': dir_dst}
    )
    if _mode == 2:
        worker_scan_destination_directories = Worker(
            target=scan_destination_directories,
            kwargs={'dir_dst': dir_dst}
        )
        worker_scan_destination_directories.start()
    worker_scan_source.start()
    worker_scan_destination.start()
    _files_src = await worker_scan_source.join()
    _files_dst = await worker_scan_destination.join()
    if _mode == 2:
        _directories_dst = await worker_scan_destination_directories.join()
    # debug: display lists
    print(f'{get_dt()} {cprint.color(s=f"[SCAN] [SOURCE] [FILES]", c=c_tag)} {cprint.color(s=_files_src, c=c_debug)}\n' if shift_dataclass.debug is True else "", end="")
    print(f'{get_dt()} {cprint.color(s=f"[SCAN] [DESTINATION] [FILES]", c=c_tag)} {cprint.color(s=_files_dst, c=c_debug)}\n' if shift_dataclass.debug is True else "", end="")
    # display lengths of lists and time
    print(f'{get_dt()} {cprint.color(s=f"[SCAN] [TIME]", c=c_tag)} {cprint.color(s=time.perf_counter()-t_scandir, c=c_data)}\n' if shift_dataclass.verbose is True else "", end="")
    print(f'{get_dt()} {cprint.color(s=f"[SCAN] [SOURCE] [FILES]", c=c_tag)} {cprint.color(s=len(_files_src[0]), c=c_data)}')
    print(f'{get_dt()} {cprint.color(s=f"[SCAN] [DESTINATION] [FILES]", c=c_tag)} {cprint.color(s=len(_files_dst[0]), c=c_data)}')
    if _mode == 2:
        print(f'{get_dt()} {cprint.color(s=f"[SCAN] [DESTINATION] [DIRECTORIES]", c=c_tag)} {cprint.color(s=len(_directories_dst[0]), c=c_data)}')

    # stat source and destination (2x async multi-processes)
    print(f'{get_dt()} {cprint.color(s=f"[RUNNING] [STAT]", c=c_tag)}')
    t_stat = time.perf_counter()
    chunks_files_src = tabulate_helper2.chunk_data(data=_files_src[0], chunk_size=128)
    worker_stat_results_src = Worker(
        target=main_worker_stat_results,
        args=(chunks_files_src,),
        kwargs={}
    )
    stat_results_dst = []
    if _mode == int(1) or _mode == int(2):
        chunks_files_dst = tabulate_helper2.chunk_data(data=_files_dst[0], chunk_size=128)
        worker_stat_results_dst = Worker(
            target=main_worker_stat_results,
            args=(chunks_files_dst,),
            kwargs={}
        )
        # start destination scandir worker
        worker_stat_results_dst.start()
    # start source scandir worker
    worker_stat_results_src.start()
    # wait for results
    stat_results_src = await worker_stat_results_src.join()
    if _mode == int(1) or _mode == int(2):
        stat_results_dst = await worker_stat_results_dst.join()

    # un-chunk and qualify/disqualify lists: (vet results while un-chunking the list)
    stat_results_src[:] = [item for sublist in stat_results_src for item in sublist if item is not None and len(item) == 3 and isinstance(item[1], float) and isinstance(item[2], int)]
    stat_results_dst[:] = [item for sublist in stat_results_dst for item in sublist if item is not None and len(item) == 3 and isinstance(item[1], float) and isinstance(item[2], int)]
    # display results if in debug mode
    print(f'{get_dt()} [STAT SRC FILES] {stat_results_src}\n' if shift_dataclass.debug is True else "", end="")
    print(f'{get_dt()} [STAT DST FILES] {stat_results_dst}\n' if shift_dataclass.debug is True else "", end="")
    # display stat files time
    print(f'{get_dt()} {cprint.color(s=f"[STAT] [TIME]", c=c_tag)} {cprint.color(s=time.perf_counter()-t_stat, c=c_data)}\n' if shift_dataclass.verbose is True else "", end="")

    # initiate lists to populate with lists of upcoming tasks
    _copy_tasks = []
    _update_tasks = []
    _delete_tasks = []

    # enumerate tasks ahead (3x async multi-processes)
    print(f'{get_dt()} {cprint.color(s=f"[RUNNING] [ENUMERATION]", c=c_tag)}')
    t_enum = time.perf_counter()
    chunks_files_src = tabulate_helper2.chunk_data(data=stat_results_src, chunk_size=128)
    worker_enum_copy_tasks = Worker(
        target=main_enum_copy_tasks,
        args=(chunks_files_src, {'dir_src': dir_src, 'dir_dst': dir_dst}),
        kwargs={}
    )
    worker_enum_update_tasks = Worker(
        target=main_enum_update_tasks,
        args=(chunks_files_src, {'dir_src': dir_src, 'dir_dst': dir_dst}),
        kwargs={}
    )
    chunks_files_dst = tabulate_helper2.chunk_data(data=stat_results_dst, chunk_size=128)
    worker_enum_delete_tasks = Worker(
        target=main_enum_delete_tasks,
        args=(chunks_files_dst, {'dir_src': dir_src, 'dir_dst': dir_dst}),
        kwargs={}
    )

    # start enumeration workers
    worker_enum_copy_tasks.start()
    if _mode == int(1) or _mode == int(2):
        worker_enum_update_tasks.start()
    if _mode == int(2):
        worker_enum_delete_tasks.start()

    # wait for results back from enumeration workers
    _copy_tasks = await worker_enum_copy_tasks.join()
    if _mode == int(1) or _mode == int(2):
        _update_tasks = await worker_enum_update_tasks.join()
    if _mode == int(2):
        _delete_tasks = await worker_enum_delete_tasks.join()

    # handle enumeration results: copy
    if None not in _copy_tasks:
        # un-chunk and qualify/disqualify lists: (vet results while un-chunking the list)
        _copy_tasks[:] = [item for sublist in _copy_tasks for item in sublist if item is not None and len(item) == 5 and isinstance(item[1], float) and isinstance(item[2], int) and isinstance(item[3], str) and isinstance(item[4], str)]
    else:
        _copy_tasks = []
    # handle enumeration results: update
    if _mode == int(1) or _mode == int(2):
        if None not in _update_tasks:
            # un-chunk and qualify/disqualify lists: (vet results while un-chunking the list)
            _update_tasks[:] = [item for sublist in _update_tasks for item in sublist if item is not None and len(item) == 5 and isinstance(item[1], float) and isinstance(item[2], int) and isinstance(item[3], str) and isinstance(item[4], str)]
        else:
            _update_tasks = []
    # handle enumeration results: delete
    if _mode == int(2):
        if None not in _delete_tasks:
            # un-chunk and qualify/disqualify lists: (vet results while un-chunking the list)
            _delete_tasks[:] = [item for sublist in _delete_tasks for item in sublist if item is not None and len(item) == 5 and isinstance(item[1], float) and isinstance(item[2], int) and isinstance(item[3], str) and isinstance(item[4], str)]
        else:
            _delete_tasks = []

    # display results if in debug mode
    print(f'{get_dt()} [ENUM COPY FILES] {_copy_tasks}\n' if shift_dataclass.debug is True else "", end="")
    print(f'{get_dt()} [ENUM UPDATE FILES] {_update_tasks}\n' if shift_dataclass.debug is True else "", end="")
    print(f'{get_dt()} [ENUM DELETE FILES] {_delete_tasks}\n' if shift_dataclass.debug is True else "", end="")
    # display enumeration time
    print(f'{get_dt()} {cprint.color(s=f"[ENUMERATION] [TIME]", c=c_tag)} {cprint.color(s=time.perf_counter()-t_enum, c=c_data)}\n' if shift_dataclass.verbose is True else "", end="")

    # display number of tasks ahead
    print(f'{get_dt()} {cprint.color(s="[TASKS]", c=c_tag)} {cprint.color(s="( Copy: ", c=c_data)} {cprint.color(s=(str(len(_copy_tasks))), c="G")} {cprint.color(s=") ( Update:", c=c_data)} {cprint.color(s=(str(len(_update_tasks))), c="B")} {cprint.color(s=") ( Delete:", c=c_data)} {cprint.color(s=(str(len(_delete_tasks))), c="Y")} {cprint.color(s=") (Total:", c=c_data)} {cprint.color(s=str(len(_copy_tasks)+len(_update_tasks)+len(_delete_tasks)), c="W")} {cprint.color(s=")", c=c_data)}')

    # storage check: calculate bytes needed in destination
    total_sz = int(0)
    for sublist in _copy_tasks:
        total_sz += int(sublist[2])
    for sublist in _update_tasks:
        total_sz += int(sublist[2])
    if _dataclass.no_bin is False:
        for sublist in _delete_tasks:
            total_sz += int(sublist[2])

    # storage check: display bytes required in destination and free bytes in destination
    print(f'{get_dt()} {cprint.color(s=f"[DISK]", c=c_tag)} {cprint.color(s=F"Available storage needed: {str(convert_bytes(total_sz))}. (Available: {str(convert_bytes(free_disk_space(_path=dir_dst)))})", c=c_data)}')

    # storage check: check if there is enough space in the destination
    if await asyncio.to_thread(out_of_disk_space, _path=dir_dst, _size=total_sz) is False:

        # initiate lists for final results
        _copied_final_results, _updated_final_results, _deleted_final_results = [], [], []

        # initiate lists for final results further sorted
        _copied, _updated, _deleted, _failed_copy, _failed_update, _failed_delete = [], [], [], [], [], []

        # todo: optional prompt
        if await user_accept(_dataclass=_dataclass) is True:

            # display final tasks are running
            print(f'{get_dt()} {cprint.color(s=f"[RUNNING] [MAIN OPERATION]", c=c_tag)}')

            # run copy
            chunks = tabulate_helper2.chunk_data(data=_copy_tasks, chunk_size=100)
            for chunk in chunks:
                tasks = []
                [tasks.append(asyncio.create_task(async_write(_data=sublist, _dataclass=_dataclass))) for sublist in chunk]
                _copied_final_results.append(await asyncio.gather(*tasks))

            # run update
            chunks = tabulate_helper2.chunk_data(data=_update_tasks, chunk_size=100)
            for chunk in chunks:
                tasks = []
                [tasks.append(asyncio.create_task(async_write(_data=sublist, _dataclass=_dataclass))) for sublist in chunk]
                _updated_final_results.append(await asyncio.gather(*tasks))

            # run delete
            tasks = []
            [tasks.append(asyncio.create_task(async_remove_file(_data=sublist, _dataclass=_dataclass))) for sublist in _delete_tasks]
            _deleted_final_results.append(await asyncio.gather(*tasks))

            # finally remove dirs not in source
            if _mode == int(2):
                [_remove_dirs(_path=item_dir, _dataclass=_dataclass) for item_dir in _directories_dst[0]]

        else:
            print(f'{get_dt()} {cprint.color(s=f"[ABORTING] [MAIN OPERATION]", c=c_tag)}')

        # unpack results
        _copied_final_results[:] = [item for sublist in _copied_final_results for item in sublist]
        _updated_final_results[:] = [item for sublist in _updated_final_results for item in sublist]
        _deleted_final_results[:] = [item for sublist in _deleted_final_results for item in sublist]

        # sort results
        [_copied.append(sublist) for sublist in _copied_final_results if sublist[-1] is True and sublist[4] == '[COPYING]']
        [_updated.append(sublist) for sublist in _updated_final_results if sublist[-1] is True and sublist[4] == '[UPDATING]']
        [_deleted.append(sublist) for sublist in _deleted_final_results if sublist[-1] is True and sublist[4] == '[DELETING]']
        [_failed_copy.append(sublist) for sublist in _copied_final_results if sublist[-1] is not True and sublist[4] == '[COPYING]']
        [_failed_update.append(sublist) for sublist in _updated_final_results if sublist[-1] is not True and sublist[4] == '[UPDATING]']
        [_failed_delete.append(sublist) for sublist in _deleted_final_results if sublist[-1] is not True and sublist[4] == '[DELETING]']

        # display final results summary
        print(f'{get_dt()} {cprint.color(s="[SUCCEEDED]", c=c_tag)} {cprint.color(s="( Copied: ", c=c_data)} {cprint.color(s=(str(len(_copied))), c="G")} {cprint.color(s=") ( Updated:", c=c_data)} {cprint.color(s=(str(len(_updated))), c="B")} {cprint.color(s=") ( Deleted:", c=c_data)} {cprint.color(s=(str(len(_deleted))), c="Y")} {cprint.color(s=") (Total:", c=c_data)} {cprint.color(s=(str(len(_copied) + len(_updated) + len(_deleted))), c="W")} {cprint.color(s=")", c=c_data)}')
        print(f'{get_dt()} {cprint.color(s="[FAILED]", c=c_tag)} {cprint.color(s="( Copy: ", c=c_data)} {cprint.color(s=(str(len(_failed_copy))), c=c_data)} {cprint.color(s=") ( Update:", c=c_data)} {cprint.color(s=(str(len(_failed_update))), c=c_data)} {cprint.color(s=") ( Delete:", c=c_data)} {cprint.color(s=(str(len(_failed_delete))), c=c_data)} {cprint.color(s=") ( Total:", c=c_data)} {cprint.color(s=(str(len(_failed_copy) + len(_failed_update) + len(_failed_delete))), c=c_data)} {cprint.color(s=")", c=c_data)}')

    else:
        print(f'{get_dt()} {cprint.color(s="[WARNING] Not enough disk space! Free up available space.", c="R")}')


if __name__ == '__main__':

    # used for compile time
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

    # debug
    debug = False
    if '--debug' in sys.argv:
        debug = True

    # debug
    no_input = False
    if '-y' in sys.argv:
        no_input = True

    # stdin
    stdin = list(sys.argv)
    print(f'\n{get_dt()} [STDIN RAW] {stdin}\n' if debug is True else "", end="")

    # verbosity
    verbose = False
    if '-v' in stdin:
        verbose = True

    # help
    if '-h' in stdin:
        shift_help.display_help()
    else:
        # mode
        mode = False
        if '-copy' in stdin:
            mode = int(0)
        elif '-update' in stdin:
            mode = int(1)
        elif '-mirror' in stdin:
            mode = int(2)

        # use recycle bin
        no_bin = False
        if '--no-bin' in stdin:
            no_bin = True

        # Note:    Extra single backslash creates a single entry in stdin which includes not only source but also -d
        #          and -d some of -d path (if -s and -d specified last). This is expected behaviour and is in
        #          my opinion concerning and so will be fixed in later releases.
        #          Example (don't do this):
        #
        #          Command: ... -s 'D:\Documents\Work\1. Projects\' -d 'X:\Documents\Work\1. Projects\'
        #
        #          Result:  -s = 'D:\Documents\Work\1. Projects" -d X:\Documents\Work\1.\'
        #
        #          Although this will not result in a valid path on most systems it is still not recommended and
        #          so currently it is recommended to omit a trailing single backslash when specifying -s, -d.
        #
        #          Input sanitation is only required for -s and -d because all other input arguments translate
        #          to predefined hardcoded bool/int values and have hardcoded defaults.
        #

        # source todo: testing with different paths (like network paths for example) before making -s valid
        source = None
        if '-s' in stdin:
            # get source path
            source_check = stdin[stdin.index('-s')+1]
            # strip single/double quotes
            source_check = source_check.strip('"')
            source_check = source_check.strip("'")
            # append backslash if not endswith backslash
            if not source_check.endswith('\\'):
                source_check = source_check+'\\'
            # check path exists
            if os.path.exists(source_check):
                # check path is directory
                if os.path.isdir(source_check):
                    # finally allow source to be set
                    source = source_check

        # destination  todo: testing with different paths (like network paths for example) before making -d valid
        destination = None
        if '-d' in stdin:
            # get destination path
            destination_check = stdin[stdin.index('-d')+1]
            # strip single/double quotes
            destination_check = destination_check.strip('"')
            destination_check = destination_check.strip("'")
            # append backslash if not endswith backslash
            if not destination_check.endswith('\\'):
                destination_check = destination_check+'\\'
            # check path exists
            if os.path.exists(destination_check):
                # check path is directory
                if os.path.isdir(destination_check):
                    # finally allow destination to be set
                    destination = destination_check

        # final checks: (a mode was specified and -s, -d are valid)
        if str(mode).isdigit():
            if source:
                if destination:
                    shift_dataclass = ShiftDataClass(debug=debug,
                                                     verbose=verbose,
                                                     no_input=no_input,
                                                     mode=mode,
                                                     source=source,
                                                     destination=destination,
                                                     no_bin=no_bin)
                    asyncio.run(main(_dataclass=shift_dataclass))
                else:
                    print(f'{get_dt()} {cprint.color(s="[INVALID] A valid destination path must be specified (-d) with trailing escape characters omitted. See -h for help.", c="R")}')
            else:
                print(f'{get_dt()} {cprint.color(s="[INVALID] A valid source path must be specified (-s) with trailing escape characters omitted. See -h for help.", c="R")}')
        else:
            print(f'{get_dt()} {cprint.color(s="[INVALID] A mode must be specified. See -h for help.", c="R")}')
        print('')
        print('')
