import shutil
from pathlib import Path

from directory import DirectoryIter


def rename_dirs(target: Path, experiment_names: list):
    """
    Принимает путь к папке (target), в которой переименовываются все папки по списку (experiment_names).
     Исходные папки находятся по алфавитному порядку - и целевой список названий тоже должен идти по алфавитному порядку.

    :param target:
    :type target:
    :param experiment_names:
    :type experiment_names:
    :return:
    :rtype:
    """
    # Заменяем имена в существующей директории
    current_dirs = list(target.iterdir())
    for source_dir, target_name in zip(current_dirs, experiment_names):
        target_dir = target / target_name
        if source_dir != target_dir:
            print(f'В папке "{target}" заменил "{source_dir.name}" на "{target_dir.name}"')
            shutil.move(source_dir, target_dir)
    # Создаём нужные папки, которые ещё отсутствуют
    for target_name in experiment_names:
        target_dir = target / target_name
        if not target_dir.exists():
            target_dir.mkdir(exist_ok=True)
            print(f'Создал в папке "{target}" папку "{target_dir.name}" ')


if __name__ == '__main__':
    target = r'D:\!Science\Физтех\Циклирования\Эксперименты_метро'
    target = DirectoryIter(target)

    # Формируем список названий этапов
    experiment_start = [
        'Испытание рабочих характеристик',
        'Подготовка к циклированиям',
    ]
    experiment_repeats = [
        'Испытание рабочих характеристик',
        'Циклирование 28 дней'
    ]
    n_cycles = 6  # Количество повторений циклирований
    experiment_names = []
    for i, steps in enumerate([experiment_start] + [experiment_repeats] * n_cycles):
        experiment_names.extend([name + f' - этап {i}' for name in steps])
    experiment_names = [f'{str(i).zfill(2)}.' + name for i, name in enumerate(experiment_names, 1)]

    # Создаём тестовые папки
    # for i, name_dir in enumerate(experiment_names[:7]):
    #     new_dir = target.path / ('wrong ' + name_dir)
    #     test_dir = new_dir / f'test {i}' / f'file{i}'
    #     test_dir.mkdir(exist_ok=True, parents=True)

    # Находим папки на нужном углублении.
    depth = 2
    for directory in target.path.rglob('*'):
        if directory.is_dir() and len(directory.relative_to(target.path).parts) == depth:
            print(directory)
            rename_dirs(directory, experiment_names)
