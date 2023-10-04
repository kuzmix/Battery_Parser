"""
This module will provide functions for splitting, parsing battery CC/CV cycles for  modelling
"""
import pandas as pd


class Check_pattern: #TODO перенести в файл с обработкой (который будет)
    """
    Creates object that check if given
    Args:
        pattern:str string of '+', '-' or '0' for positive, negative and zero value
    """

    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, split: list):
        assert len(self.pattern) == len(split)
        checks = [self.check_element(element, condition)
                  for element, condition
                  in zip(split, self.pattern)]
        return all(checks)

    @staticmethod
    def check_element(element, condition):
        if condition == '0':
            return element == 0
        elif condition == '+':
            return element > 0
        elif condition == "-":
            return element < 0


def generate_statistics(data: pd.DataFrame,
                        group_marker="Step",
                        statistics_pattern={'I': ['mean', 'std'],
                                            'Time': ['max', 'diff'],
                                            'E': 'mean',
                                            'T':['min', 'max']}):
    """
    Group dataframe by 'group_marker' and summarize explicit columns with given methods.
    'statistic_pattern' configure statistic results.
    Standard pattern include Current, time and voltage summarization.
    Summarization methods are currently 'mean', 'std', 'max', 'min'.
    Args:
        data (pd.Dataframe): cycle/experiment/etc dataframe.
        group_marker (str or list[str]): column (columns) which will be used as group marker
                                        (argument for df.groupby() )
        statistics_pattern (dict): str:str, where column is column name you want to summarize,
                                    and value is method you want to use for summarization
                                    (mean, std, max, min)

    Returns: pd.Dataframe, with total statistics via marker.

    """
    grouped_data = data.groupby(group_marker)
    frame_dict = {}
    for column, methods in statistics_pattern.items():
        frame_dict.update(column_statistics(grouped_data, column, methods))
    df = pd.DataFrame(frame_dict)
    return df


def column_statistics(grouped_data: pd.DataFrame.groupby, column: str, methods: str | list):
    """
    Takes column name and method|list of methods for summary, and create dict with
    given entries - one or more entries
    Args:
        grouped_data (pd.Dataframe): all dataframe grouped by some method
        column (str): column name
        methods (str|list[str]): method(s) to summarize

    Returns:
        (dict) of series for every statistic method
    """
    if isinstance(methods, str):
        return column_statistics_step(grouped_data, column, methods)

    if isinstance(methods, list):
        join_dict = {}
        for method in methods:
            join_dict.update(column_statistics_step(grouped_data, column, method))
        return join_dict


def column_statistics_step(grouped_data: pd.DataFrame, column: str, method: str):
    """
    Create dict entry for given method and column, in a way like
    "columnName_method":pd.Series with result
    Args:
        grouped_data (): group object (or just Dataframe maybe) for summarization
        column (str): Column name
        method (str): method name: min, max, mean, std, diff

    Returns:
            (dict) with one entry - statistic summary for method and column. Key = column_method
    """
    return {'_'.join([column, method]): summarize_grouper_fragment(grouped_data[column], method)}


def summarize_grouper_fragment(data_slice, method: str = 'mean'):
    """
    One column (or maybe more, I test it only with Series) and text method
    make statistic for given data_slice with given method

    Args:
        data_slice (pd.Series.groupby): grouper object for one Series
        method (str): method marker. Handle 'mean', 'std', 'max', 'min', 'diff' methods

    Returns:
        pd.Series
    """
    match method:
        case 'mean':
            return data_slice.mean()
        case 'std':
            return data_slice.std()
        case 'max':
            return data_slice.max()
        case 'min':
            return data_slice.min()
        case 'diff':
            index_name = data_slice.keys
            column_name = data_slice.nth(0).name
            dict_diff = {step[0]: step[1].diff().mean() for step in data_slice}
            output = pd.Series(dict_diff, name=column_name)
            output.index.name = index_name
            return output
        case _:
            raise ValueError
