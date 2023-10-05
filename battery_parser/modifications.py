import pandas as pd
import pandas.api.types


def rename_columns(dataframe: pd.DataFrame,
                   rename: dict = None,
                   default_rename=True,
                   inplace=True):
    """
    Change column names from specific to general. Have default dict for usual changes.
    You also can use or not default dict, and add renaming dict yourself. Renaming works like
    if you find column name in keys of dict, you rename it.
    Renaming dict may be any size.

    Default changes:
    'Record Index':'Index',
    'Cur(A)':'I',
    'Voltage(V)':'E',
    'CapaCity(Ah)':'Q',
    'Energy(Wh)':'Energy',
    'Absolute Time':'Datetime',
    'Relative Time(h:min:s.ms)':'Time',
    'Auxiliary channel TU1 T(°C)':'T'

    Args:
        dataframe (Dataframe): dataframe for renaming columns
        rename (dict): some specific renaming patterns
        default_rename (bool): Should you use default rename or not.
         Rename dict rewrites default dict
        inplace (bool): modify given dataframe or return modified copy of dataframe

    Returns:
        None or modified DataFrame
    """
    rename_dict = {}
    if default_rename:
        default_rename_dict = {'Record Index':'Index', #TODO should be transfered to specific file
                               'Cur(A)':'I',
                               'Voltage(V)':'E',
                               'CapaCity(Ah)':'Q',
                               'Energy(Wh)':'Energy',
                               'Absolute Time':'Datetime',
                               'Relative Time(h:min:s.ms)':'Time',
                               'Auxiliary channel TU1 T(°C)':'T'
                               }
        rename_dict.update(default_rename_dict)

    if rename:
        rename_dict.update(rename)

    if inplace:
        dataframe.rename(mapper=rename_dict, axis=1, inplace=True)
    else:
        return dataframe.rename(mapper=rename_dict, axis=1)


def parse_time(dataframe:pd.DataFrame,
               time_column:str=None,
               time_unit:str='S',
               datetime_column:str=None,
               **kwargs):
    """
    Function that parse time columns to seconds(float)
    and datetime columns (in object or text) to datetime object.
    Args:
        dataframe (): dataframe to modify
        time_column (): columns that have time, transfers to float64 seconds format
        time_unit (): if time column type is numeric, specifies units for transfer
        datetime_column (): columns that have datetime forms, transfer to datetime object
        **kwargs (): arguments for datetime parser

    Returns:
        None.
    """
    if time_column:
        if pandas.api.types.is_numeric_dtype(dataframe[time_column]):
            dataframe[time_column] = pd.to_timedelta(dataframe[time_column], unit=time_unit)
        else:
            dataframe[time_column] = pd.to_timedelta(dataframe[time_column])

        dataframe[time_column] = dataframe[time_column].dt.total_seconds()

    if datetime_column:
        dataframe[datetime_column] = pd.to_datetime(dataframe[datetime_column], **kwargs)

