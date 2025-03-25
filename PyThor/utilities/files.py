import os
from PyThor.config.config import save_folder, cache_folder

if not save_folder.exists():
    os.mkdir(save_folder)
if not cache_folder.exists():
    os.mkdir(cache_folder)


def rm_grib_files():
    """
    Delete all the grib (and corresponding .idx files) files that PyThor generates during its runtime.
    """
    try:
        files = os.listdir(save_folder)
        for f in files:
            os.remove(save_folder + f)
        os.rmdir(save_folder)
    except FileNotFoundError:
        return


def rm_cache_files():
    """
    Delete all the cached query results that PyThor generates during its runtime.
    """
    try:
        files = os.listdir(cache_folder)
        for f in files:
            os.remove(cache_folder + f)
        os.rmdir(cache_folder)
    except FileNotFoundError:
        return
