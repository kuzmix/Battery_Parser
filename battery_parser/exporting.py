import os

import pandas as pd


def save_experiment(data: pd.DataFrame, filepath: str, index = False, **kwargs):
    """
    Saves experiment as csv to given path. kwargs for saving function df.to_csv
    Args:
        data (): dataframe to save
        filepath (): path for saving

    Returns:
        None
    """
    directory, filename = os.path.split(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    data.to_csv(filepath, index = index, **kwargs)


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
