import os.path
from pathlib import Path

import NewareNDA as N
import numpy as np
import pandas as pd

import battery_parser as bp


class Experiment:
    def __init__(self, path=None, pouch=None, channel=None):
        self.path = path
        self.pouch = pouch
        self.channel = channel
        self.data = None
        self.statistics = None
        self.segments = {}


def find_segments(df, column_name, pattern):
    # Переводим колонку в массив NumPy
    arr = df[column_name].to_numpy()

    # Искомый шаблон
    if not isinstance(pattern, np.ndarray):
        pattern = np.array(pattern)

    # Создаём матрицу окон размером len(pattern)
    shape = (arr.size - len(pattern) + 1, len(pattern))
    strides = (arr.strides[0], arr.strides[0])
    windows = np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)

    # Сравниваем каждое окно с шаблоном
    matches = np.all(windows == pattern, axis=1)

    # Получаем начальные индексы совпадений
    match_indices = np.where(matches)[0]

    # Результат
    return [df.iloc[i:i + len(pattern)] for i in match_indices]


def process_segment_dfs(segment_dfs, func):
    """
    Применяет func ко всем DataFrame-сегментам и собирает результаты в один DataFrame.

    segment_dfs : список DataFrame-объектов (срезов)
    func        : функция, применяемая к каждому сегменту. Должна возвращать словарь или Series.

    Возвращает: итоговый DataFrame с результатами обработки всех сегментов.
    """
    results = []
    for i, seg_df in enumerate(segment_dfs):
        result = func(seg_df)
        if isinstance(result, dict) or isinstance(result, pd.Series):
            result = dict(result)
        else:
            raise ValueError("Функция должна возвращать словарь или Series.")
        results.append(result)

    return pd.DataFrame(results)


def analyze_cycle_segment(segment_df):
    """
    Анализирует сегмент DataFrame:
    - находит максимальную температуру в колонке 'T1_max'
    - находит значение 'Discharge_Capacity(mAh)_max' для строки,
      где 'Status_unique_values' == 'CC_DChg'

    Возвращает словарь с результатами.
    """
    result = {}

    # Максимальная температура
    result["T1_max"] = segment_df["T1_max"].max()
    result["Date_min"] = segment_df["Timestamp_min"].min()
    # Значение Discharge_Capacity(mAh)_max для первой строки с CC_DChg
    mask = segment_df["Status_unique_values"] == "CC_DChg"
    discharge_rows = segment_df[mask]

    if not discharge_rows.empty:
        result["Discharge_Capacity"] = discharge_rows["Discharge_Capacity(mAh)_max"].iloc[0]
    else:
        result["Discharge_Capacity"] = None  # или np.nan

    return result


def statistic_generation():
    directory = r'D:\!Science\Analysis\Electrochem\2024 Na-ion\2025-01-10 target SoH cycling\2025-01-10 первое циклирование'  # Папка где лежат все эксперименты
    files = bp.importing.list_files(directory=directory, filetype='ndax')  # Список файлов
    pattern = r'(\d{3}-\d-\d)'
    columns = ['channel']
    parser = bp.importing.Regex_parse()
    result = parser(strings=files, pattern=pattern, column_names=columns)
    mapping = pd.read_excel(r"D:\!Science\Analysis\Electrochem\2024 Na-ion\2025-01-10 target SoH "
                            r"cycling\Соответствие_каналов_и_аккумуляторов.xlsx", sheet_name='Соответствие')
    result = pd.merge(result, mapping, on=['channel'], how='left')
    experiments = {}
    statistic_pattern = {'Current(mA)': ['mean', 'std'],
                         'Status':'unique_values',
                         'Step': 'mean',
                         'Charge_Capacity(mAh)': 'max',
                         'Discharge_Capacity(mAh)': 'max',
                         'Step_Index': 'mean',
                         'Index':'min',
                         'Time':['range', 'diff'],
                         'Voltage': ['mean', 'first', 'last'],
                         'T1': ['min', 'max'],
                         'Timestamp': 'min'}
    save_dir = os.path.join(directory, 'statistics')
    for _, i in result.iterrows():
        experiment = Experiment(path=i['path'], pouch=i['pouch'], channel=i['channel'])
        experiments[experiment.pouch] = experiment
        experiment.data = N.read(experiment.path, log_level='DEBUG')
        experiment.statistics = bp.generate_statistics(experiment.data,
                                                       group_marker='Step',
                                                       statistics_pattern=statistic_pattern)
        bp.exporting.save_experiment(experiment.statistics, os.path.join(save_dir, experiment.pouch + '.csv'),
                                     index=False)


def load_statistics():
    directory = r'D:\!Science\Analysis\Electrochem\2024 Na-ion\2025-01-10 target SoH cycling\2025-01-10 первое циклирование\statistics'
    files = bp.importing.list_files(directory=directory, filetype='csv')
    statistics = {}
    for filepath in files:
        pouch = Path(filepath).stem
        experiment = Experiment(path=filepath, pouch=pouch, channel=None)
        statistics[experiment.pouch] = experiment
        experiment.statistics = bp.exporting.load_experiment(filepath)
    return statistics


def calculate_soh(df, capacity):
    try:
        df['SoH'] = df['Discharge_Capacity'] / capacity
    except:
        pass


def calculate_soh2(df, capacity):
    try:
        df['SoH2'] = df['Discharge_Capacity'] / capacity
    except:
        pass


if __name__ == '__main__':
    # statistic_generation()
    statistics = load_statistics()
    pattern_cycles = [6, 7, 8, 9, 10]
    pattern_start_cycles = [1, 2, 3, 4]
    pattern_test_cycles = [28, 29, 30, 31]
    start_cycles = {}
    test_cycles = {}
    cycles = {}
    all_cycles = {}
    for pouch, experiment in statistics.items():
        experiment.segments['cycles'] = find_segments(experiment.statistics, 'Step_Index_mean', pattern_cycles)
        experiment.segments['start_cycles'] = find_segments(experiment.statistics, 'Step_Index_mean',
                                                            pattern_start_cycles)
        experiment.segments['test_cycles'] = find_segments(experiment.statistics, 'Step_Index_mean',
                                                           pattern_test_cycles)

        cycles[experiment.pouch] = process_segment_dfs(experiment.segments['cycles'], analyze_cycle_segment)
        start_cycles[experiment.pouch] = process_segment_dfs(experiment.segments['start_cycles'], analyze_cycle_segment)
        test_cycles[experiment.pouch] = process_segment_dfs(experiment.segments['test_cycles'], analyze_cycle_segment)
        calculate_soh(cycles[experiment.pouch], start_cycles[experiment.pouch]['Discharge_Capacity'][0])
        calculate_soh(test_cycles[experiment.pouch], start_cycles[experiment.pouch]['Discharge_Capacity'][0])
        all_cycles[experiment.pouch] = pd.concat(
            [cycles[experiment.pouch], start_cycles[experiment.pouch], test_cycles[experiment.pouch]],
            ignore_index=True).sort_values(by='Date_min').reset_index(drop=True)
        calculate_soh2(all_cycles[experiment.pouch], all_cycles[experiment.pouch]['Discharge_Capacity'].max())
        bp.exporting.save_experiment(all_cycles[experiment.pouch], os.path.join(
            r'D:\!Science\Analysis\Electrochem\2024 Na-ion\2025-01-10 target SoH cycling\Данные 2025-05-30',
            'processing', experiment.pouch + '.csv'), index=False)
        bp.exporting.save_experiment(all_cycles[experiment.pouch].iloc[[-1]], os.path.join(
            r'D:\!Science\Analysis\Electrochem\2024 Na-ion\2025-01-10 target SoH cycling\Данные 2025-05-30',
            'processing_last', experiment.pouch + '.csv'), index=False)
        bp.exporting.save_experiment(start_cycles[experiment.pouch], os.path.join(
            r'D:\!Science\Analysis\Electrochem\2024 Na-ion\2025-01-10 target SoH cycling\Данные 2025-05-30',
            'processing_soh', experiment.pouch + '.csv'), index=False)

    pass
