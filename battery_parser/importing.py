import os
import re

import pandas as pd


def list_files(directory: str, filetype: str | list[str]):
    """
    Create list of all files in directory (without recurrent walking in dirs)
    with given file format (filetype)
    Args:
        directory (str of path-like obj): directory for file search
        filetype (str|list): necessary file formats

    Returns:
        [list] of all files with selected
    """
    if isinstance(filetype, str):  # for easier check of formats
        filetype = [filetype]
    filetypes = ['.' + f for f in filetype]
    files = []
    for root, folders, _files in os.walk(directory):
        select = [os.path.join(root, file) for file in _files if os.path.splitext(file)[-1] in filetypes]
        files.extend(select)
    files.sort(key=lambda x:x.split('\\')[-1])
    return files


def import_xls(filepath: str,
               data_name_pattern='Detail_',
               temp_name_pattern='DetailTemp_',
               temp_column_pattern='T(°C)'):
    f"""
    Get cycling data and temperature data from Excel file.
    Specific for multiple sheet structure, where all data sheets have in name
    a string like {data_name_pattern} (specified) and go one by another
    temperature have in name string like {temp_name_pattern} (specified) and go one by another.
    Temperature column name should consist of {temp_column_pattern} to add temperature to dataframe

    Args:
        temp_name_pattern (str): Unique name pattern in sheets for temperature
        data_name_pattern (str): Unique name pattern in sheets for data
        filepath (str):path to Excel file with cycling data and/or temperature

    Returns:
        pd.Dataframe with data (and temperature if exist)
    """
    import_data = pd.read_excel(filepath, None, )
    data = extract_data_xls(import_data, data_name_pattern)
    temp = extract_data_xls(import_data, temp_name_pattern)
    if temp is not None:
        if all(isinstance(i, str) for i in temp.iloc[0]):
            temp.rename(columns=temp.iloc[0], inplace=True)
            temp.drop(temp.index[0], inplace=True)
            temp.reset_index(inplace=True, drop=True)
        temp_column = [i for i
                       in temp.columns
                       if temp_column_pattern in i]

        data = pd.concat([data, temp[temp_column]], axis=1)
    return data


def extract_data_xls(imported_data, name_pattern):
    """
    Select Excel sheets from data, and concat them to one dataframe (ignore index)
    Checks if pattern is in sheet names, if not returns None
    Args:
        imported_data (dict[DataFrame]): all sheets imported from Excel file
        name_pattern (str): what should filename have in for this data.

    Returns:
        pd.DataFrame with all concatenated data or None if no sheets found
    """
    data_lists = select_sheets_xls(imported_data, name_pattern)
    if data_lists:
        data = pd.concat(data_lists, ignore_index=True)
        return data
    else:
        return None


def select_sheets_xls(imported_data: dict[pd.DataFrame],
                      name_pattern: str):
    """
    Finds all data sheets that have pattern in names.
    Args:
        imported_data (dict[pd.DataFrame]): all sheets from Excel
        name_pattern (str): pattern in sheet name

    Returns:
        list of data sheets with current pattern in name
    """
    select_lists = [imported_data[i] for i
                    in imported_data.keys()
                    if name_pattern in i]
    return select_lists


class Regex_parse:
    def __init__(self):
        pass

    def __call__(self, *, strings=None, pattern=None, column_names=None):
        """

        Args:
            strings ():
            pattern ():
            column_names ():

        Returns:

        """
        assert isinstance(pattern, str)
        assert isinstance(column_names, list)
        assert isinstance(strings, list)
        for string in strings:
            assert isinstance(string, str)
        self._parse_result = []
        for string in strings:
            single_parse = self._parser(pattern, string)
            self._parse_result.extend(single_parse)
        column_names.append('Path')
        result = self._result_creator(self._parse_result, column_names)
        return result

    @staticmethod
    def _parser(pattern, string):
        """
        Takes pattern and string, applies re. function, and compose answer.
        Args:
            pattern ():
            string ():

        Returns:

        """
        result = re.findall(pattern, string)
        if len(result) != 1:
            print(f'Warning! For \n {string} \n found {len(result)} entries!')
        result = [[*i, string] for i in result]
        return result

    @staticmethod
    def _result_creator(parse_result, column_names):
        """
        Takes all results from _pattern (list) and returns structured answer.
        Args:
            parse_result ():
            column_names ():

        Returns:

        """
        result = pd.DataFrame.from_records(parse_result, columns=column_names)
        return result


def unique_re(pattern: str, files: list):
    """
    Function unique_re tests each string in given files list, and
    a)checks, how many times pattern presented in string (by printing warning if not once),
    b)return number total number of pattern entries in strings, number of unique entries and set of unique entries.
    Function is created for engineering regex patterns.
    Args:
        pattern (str): regex pattern, that you want to test on files.
        files (list):strings that you want to test with regex.

    Returns:
        (n_values - total number of pattern entries, n_unique - number of unique entries, unique_values - list of unique entries)

    """
    assert isinstance(files, list)
    assert isinstance(pattern, str)
    values = []
    for file in files:
        assert isinstance(file, str)
        found = re.findall(pattern, file)
        if len(found) != 1:
            print(f'Warning! For file \n {file} \n found {len(found)} entries!')
        values.extend(found)
    unique_values = set(values)
    n_unique = len(unique_values)
    n_values = len(values)
    return n_values, n_unique, unique_values
