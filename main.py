import battery_parser as bp

if __name__ == '__main__':
    directory = r'c:\Binary_Beaver\YandexDisk\MIPT\BP_test'  # Папка где лежат все эксперименты
    files = bp.importing.list_files(directory=directory, filetype='xls')  # Список файлов с форматом xls
    data = [bp.import_xls(filename) for filename in files]  # Список импортированных из этих экселей таблиц
    test_dataset = data[0]  # У нас одна таблица, поэтому работаем с ней
    bp.rename_columns(test_dataset)  # Изменяет названия некоторых колонок см. комментарии к функции
    bp.parse_time(test_dataset, time_column='Time', datetime_column='Datetime')  # Изменяет вид колонки времени на
    # секунды, и даты в формат datetime
    statistic_pattern = {'I':['mean', 'std'],
                         'Status':'unique_values',
                         'Index':'min',
                         'Time':['range', 'diff'],
                         'E':'mean',
                         'T':['min', 'max']}  # Можно задать формат статистики, возможные методы статистики см.
    # в комментариях к bp.generate_statistics

    statistics_data = bp.generate_statistics(test_dataset,
                                             group_marker='Step',
                                             statistics_pattern=statistic_pattern)  # Подбивает статистику по таблице
    pattern = '0-0+0-0+0'  # Задает шаблон для поиска для окон. Если хочется, можно задать параметр windows вручную
    # Формат: 0 - нулевое значение, +  больше нуля,  - меньше нуля. Передаётся строкой
    windows = bp.find_pattern(statistics_data['I_mean'], pattern=pattern)  # ищет вхождения шаблона в шагах
    merge_data = bp.extract_sequences(test_dataset, windows, time_merge = 'remove_first')  # Извлекает указанные вхождения шаблона,
    # сшивает по времени шаги либо через 'overlap', либо через gap в секундах
    bp.save_sequences(merge_data, r'c:\Binary_Beaver\YandexDisk\MIPT\BP_test',columns=['Step','Time','I','E'], sep = '\t')  # сохраняет полученные результаты.
    # доп-аргументы: 'columns' для вывода только нужных колонок; 'sep' - символ-сепаратор; и другие аргументы для pandas.DataFrame.to_csv
