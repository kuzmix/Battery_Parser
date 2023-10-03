import pandas as pd
import os


def list_files(directory:str, filetype: str | list[str]):
    """
    Create list of all files in directory (without recurrent walking in dirs)
    with given file format (filetype)
    Args:
        directory (str of path-like obj): directory for file search
        filetype (str|list): necessary file formats

    Returns:

    """
    if isinstance(filetype, str):
        filetype = [filetype]
    files = [os.path.join(directory, file) for file
             in next(os.walk(directory))[2]
             if file.split('.')[-1] in filetype]
    return files


