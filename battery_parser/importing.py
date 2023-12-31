import pandas as pd
import os


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
    files = [os.path.join(directory, file) for file
             in next(os.walk(directory))[2]
             if file.split('.')[-1] in filetype]
    return files


def import_xls(filepath: str,
               data_name_pattern = 'Detail_',
               temp_name_pattern = 'DetailTemp_'):
    """
    Get cycling data and temperature data from Excel file.
    Specific for multiple sheet structure, where all data sheets have in name
    a string like 'Detail_' (specified) and go one by another
    temperature have in name string like 'DetailTemp_' (specified) and go one by another.
    Temperature column name should consist of 'T(°C)' to add temperature to dataframe

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
        temp_column_pattern = 'T(°C)'  # specific for data format
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
