"""
Модуль предназначен для работы с файлами: сортировки, переименования, перемещения, удаления.
"""
from itertools import combinations
from pathlib import Path

from file import File


class FileList(list):
    """
    Класс для работы со списком файлов. Класс файла должен поддерживать функцию .match
    """
    file_type = File

    def __init__(self, *args, **kwargs):
        self._check_type(args)
        self._check_type(kwargs.values())

        super().__init__(*args, **kwargs)

    def _check_type(self, el):
        if hasattr(el, '__iter__'):
            for i in el:
                self._check_type(i)
        else:
            if not isinstance(el, self.file_type):
                raise TypeError('Элемент не принадлежит нужному типу.')


class DirectoryIter:
    """
    Класс для представления директории из файлов
    Итерируется.
    В него можно передать необходимый корень папку, паттерн фильтрации файлов (regex),
     класс для репрезентации файлов (базово File из battery_parser.file)
    """
    file_class = File
    file_list = FileList

    def __init__(self, dir_path: str, filter_pattern='*', ):
        self.path = Path(dir_path).resolve()
        self.filter_pattern = filter_pattern
        if not self.path.is_dir():
            raise ValueError(f"'{dir_path}' не является директорией.")
        self.files = self._get_files()

    def _get_files(self):
        """Получает все файлы в директории, включая поддиректории."""
        return self.file_list([self.file_class(f) for f in self.path.rglob(self.filter_pattern) if f.is_file()])

    def __iter__(self):
        return iter(self.files)

    def update(self):
        """Обновляет список файлов в директории"""
        self.files = self._get_files()

    def __repr__(self):
        return f"<DirectoryInfo(path={self.path}, files={len(self.files)})>"


def delete_duplicates(source: FileList,
                      duplicate_key=lambda x:x.hash,
                      delete_key=lambda x:-x.size):
    """
    Функция принимает список файлов (итерируемый, наследуемый
    от FileList или DirectoryIter).

    :param source:
    :type source:
    :param duplicate_key:
    :type duplicate_key:
    :param delete_key:
    :type delete_key:
    :return:
    :rtype:
    """
    duplicates = dict()
    for first, second in combinations(source, 2):
        if duplicate_key(first) == duplicate_key(second):
            if duplicate_key(first) in duplicates:
                duplicates[duplicate_key(first)].update([first, second])
            else:
                duplicates[duplicate_key(first)] = {first, second}
    for value in duplicates.values():
        files = list(value)
        files.sort(key=delete_key)
        for file in files[1:]:
            print('Удалён', file)
            file.delete()
    source.update()


def remove_empty_dirs(dir_path: Path):
    """Удаляет пустые папки в переданном пути класса Path"""
    # Перебираем все подкаталоги в директории
    for subdir in dir_path.iterdir():
        if subdir.is_dir():
            remove_empty_dirs(subdir)  # Рекурсивно проверяем подкаталоги

            # Если директория пустая, удаляем её
            if not any(subdir.iterdir()):
                print(f"Удаление пустой папки: {subdir}")
                subdir.rmdir()


if __name__ == '__main__':
    # Испытание DirectoryInfo
    source = r'D:\Python\Testing\Разобрать эксперименты'
    source = DirectoryIter(source)
    print(source)
    delete_duplicates(source, lambda x:x.hash, lambda x:str(x.full_path))
    remove_empty_dirs(source.path)
    print(source)
