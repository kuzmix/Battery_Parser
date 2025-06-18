import os

import pandas as pd


def save_experiment(data: pd.DataFrame, filepath: str, **kwargs):
    """
    Saves experiment as csv to given destination. kwargs for saving function df.to_csv
    Args:
        data (): dataframe to save
        filepath (): destination for saving

    Returns:
        None
    """
    directory, filename = os.path.split(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if 'index_label' not in kwargs.keys():
        kwargs['index_label'] = 'Index'
    data.to_csv(filepath, **kwargs)


def load_experiment(filepath: str, **kwargs):
    return pd.read_csv(filepath, **kwargs)


def save_sequences(splits_data: list[pd.DataFrame], dir_path: str, **kwargs):
    """
    Saves sequence of dataframes to given directory, as i.csv files where i -
    number of dataframe.
    Args:
        splits_data (): list of dataframes
        dir_path (): directory to save dataframes
        **kwargs (): arguments for df.to_csv function

    Returns:
        None
    """
    for i, experiment in enumerate(splits_data):
        filename = f'{i}.csv'
        save_path = os.path.join(dir_path, filename)
        save_experiment(experiment, save_path, **kwargs)
