import pandas as pd
import pandas.api.types


# TODO add retype functions


def rename_columns(data: pd.DataFrame,
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
        data (Dataframe): data for renaming columns
        rename (dict): some specific renaming patterns
        default_rename (bool): Should you use default rename or not.
         Rename dict rewrites default dict
        inplace (bool): modify given data or return modified copy of data

    Returns:
        None or modified DataFrame
    """
    rename_dict = {}
    if default_rename:
        default_rename_dict = {'Record Index':'Index',  # TODO should be transfered to specific file
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
        data.rename(mapper=rename_dict, axis=1, inplace=True)
    else:
        return data.rename(mapper=rename_dict, axis=1)


def parse_time(dataframe: pd.DataFrame,
               time_column: str = None,
               time_unit: str = 'S',
               datetime_column: str = None,
               **kwargs):
    """
    Function that parse time columns to seconds(float)
    and datetime columns (in object or text) to datetime object.
    Args:
        data (): data to modify
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


def check_unity(data: pd.DataFrame):
    """
    Check if dataframe have sequential indexes
    Args:
        data (): Dataframe for check

    Returns:
        bool - if indexes sequential
    """
    return all(data.index.diff().to_frame().mean() == 1)


def get_steps_data(data: pd.DataFrame, steps: list[int], specified_column='Step'):
    """
    Select steps by number (or other value) in specified column, checks if it
    is sequential and returns list of copies of steps.
    Args:
        data (): initial Dataframe for selecting data
        steps (): values for steps
        specified_column (): where values should be

    Returns:
        list[pd.Dataframe] - steps from data.
    """
    data_steps = [data[data[specified_column] == i].copy() for i in steps]
    if not check_unity(pd.concat(data_steps)):
        print('get_steps_data: Warning! Merging values are not sequential!')
    return data_steps


def merge_time(data_steps: list, merging_method = 'remove_first', column='Time'):
    """
    Make relative time from experiments cumulative by selected method
    methods: 'overlap' - drop last point for every step and
    increment became value of dropped point
    float/int - gap method with gap between steps equal to value.
    Args:
        data_steps (): list of steps
        merging_method (): 'overlap' - drop last point for step,
                            float/int - gap method, with given value
        column (): name for time column

    Returns:

    """
    match merging_method:
        case float() | int():
            return gap_merge(data_steps, merging_method, column)
        case 'remove_first'|'remove_last':
            return overlap_merge(data_steps, column = column, merging_method=merging_method)
        case None:
            return data_steps


def gap_merge(data_steps: list, gap: float | int, column='Time'):
    """
    Modify time column with gap method - consequently
    Args:
        data_steps (): list of steps
        gap (): value of gap between steps
        column (): time column name

    Returns:
        list of steps with modified time values
    """
    increment = 0
    for step in data_steps:
        step.loc[:, column] += increment
        increment = step[column].max() + gap
    return data_steps


def overlap_merge(data_steps: list[pd.DataFrame], column='Time', merging_method='remove_first'):
    """
    Modify time and overlap cycles
    delete first or last point for every step
    Args:
        data_steps (): list of steps
        column (): name for time column
        merging_method (): 'remove_first' or 'remove_last'

    Returns:

    """
    increment = 0
    for step in data_steps:
        step.loc[:, column] += increment
        increment = step[column].max()
    match merging_method:
        case 'remove_last':
            for step in data_steps[0:-1]:
                step.drop(step.tail(1).index, inplace=True)
        case 'remove_first':
            for step in data_steps[1:]:
                step.drop(step.head(1).index, inplace=True)

    return data_steps


def extract_sequences(data: pd.DataFrame,
                      sequences: list[list[int]],
                      time_merge: str | float,
                      sequence_column='Step',
                      time_column='Time'
                      ):
    """
    Returns merged dataframes, each from sequences list.
     Also merges time with selected method.
    Args:
        data (): initial dataframe
        sequences (): all hints for selection of cycles
        time_merge (): method for time merge: 'overlap' or float/int for gap method
        sequence_column (): name for sequence selection column
        time_column (): name for time column

    Returns:
        list of selected sequences
    """
    sequences_data = []
    for sequence in sequences:
        data_steps = get_steps_data(data=data, steps=sequence, specified_column=sequence_column)
        data_steps = merge_time(data_steps, time_merge, column=time_column)
        sequences_data.append(pd.concat(data_steps))
    return sequences_data
