"""
This module will provide functions for splitting, parsing battery CC/CV cycles for  modelling
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


class Check_pattern:
    """
    Creates object that check if given
    Args:
        pattern (str): string of '+', '-' or '0' for positive, negative and zero value
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
    def check_element(element, letter):
        if letter == '0':
            return element == 0
        elif letter == '+':
            return element > 0
        elif letter == "-":
            return element < 0


def generate_statistics(data: pd.DataFrame, ):
    mean = data.groupby('Step')['Cur(A)'].mean()  # TODO - make creation statistic custom.
    std = data.groupby('Step')['Cur(A)'].std()
    duration = data.groupby('Step')['Relative Time'].max()
    voltage = data.groupby('Step')['Voltage(V)'].mean()
    frame = {"Cur(A)_mean":mean,
             'Cur(A)_std':std,
             "Relative Time_max":duration,
             "Voltage(V)_mean":voltage}
    df = pd.DataFrame(frame)
    return df
