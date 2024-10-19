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

    def __init__(self, *args, file_rep=File, **kwargs):
        self.filetype = file_rep
        self.check_type(args)
        self.check_type(kwargs.values())

        super().__init__(*args, **kwargs)

    def check_type(self, el):
        if hasattr(el, '__iter__'):
            for i in el:
                self.check_type(i)
        else:
            if not isinstance(el, self.filetype):
                raise TypeError('Элемент не принадлежит нужному типу.')

    def filter(self, pattern):
        return self.__class__([i for i in self if i.path.match(pattern)])


class DirectoryIter:
    """
    Класс для представления директории из файлов
    Итерируется.
    В него можно передать необходимый корень папКУ, паттерн фильтрации файлов (regex),
     класс для репрезентации файлов (базово File из battery_parser.file)
    """

    def __init__(self, dir_path: str, filter_pattern='*', file_rep=File):
        self.path = Path(dir_path).resolve()
        self.filter_pattern = filter_pattern
        self.rep = file_rep
        if not self.path.is_dir():
            raise ValueError(f"'{dir_path}' не является директорией.")
        self.files = self._get_files()

    def _get_files(self):
        """Получает все файлы в директории, включая поддиректории."""
        return FileList([self.rep(f) for f in self.path.rglob(self.filter_pattern) if f.is_file()])

    def __iter__(self):
        return iter(self.files)

    def update(self):
        """Обновляет список файлов в директории"""
        self.files = self._get_files()

    def __repr__(self):
        return f"<DirectoryInfo(path={self.path}, files={len(self.files)})>"

    def filter(self, pattern):
        return self.files.filter(pattern)


# class DirectoryCleaner: #TODO Нужно удалить кривые счётчики.
#     """
#     Удаляет ненужные файлы
#     """
#
#     def __init__(self, source_dir: (str, DirectoryInfo), target_dir: (str, DirectoryInfo)):
#
#         self.source = source_dir
#         self.target = target_dir
#
#     def clean(self, smart_copy=False):
#         """Удаляет файлы из исходной директории, если они уже существуют в целевой директории."""
#         for file_info in self.source.files:
#             if file_info.hash in self.target.hashes and self.target.hashes[file_info.hash] == file_info.name:
#                 str_output = f"Удаление файла: {file_info.name} (существует в целевой директории)"
#                 if self.target.hashes[file_info.hash] == file_info.name:
#                     str_output += ' + совпадает с целевым по имени+'
#                 print(str_output)
#                 file_info.path.unlink()  # Удаление файла
#                 self.deleted_files_count()  # Увеличиваем счетчик удаленных файлов
#             else:
#                 if smart_copy:
#                     self.smart_copy(file_info)
#         # Удаляем пустые папки из исходной директории
#         self._remove_empty_dirs(self.source.path)
#         self.source.update()
#         self.target.update()
#
#         # Выводим количество удаленных файлов и папок
#         print(f"\nУдалено файлов: {self.deleted_files_count.i}")
#         print(f"Удалено папок: {self.deleted_dirs_count.i}")
#
#     def __setattr__(self, key, value):
#         if key in ['source', 'target', ]:
#             if isinstance(value, DirectoryInfo):
#                 super().__setattr__(key, value)
#             elif isinstance(value, str):
#                 super().__setattr__(key, DirectoryInfo(value))
#             else:
#                 raise TypeError('Directory paths are not valid.')
#
#     def check_filenames(self):
#         """
#
#         :return:
#         :rtype:
#         """
#         target_names = [f.name for f in self.target.files]
#         for file_info in self.source.files:
#             if file_info.name in target_names:
#                 if len([d for d in self.target.files if d.name == file_info.name]) > 1:
#                     print(f"Более одного совпадающего файла для {file_info.name}")
#                 for target_file in [d for d in self.target.files if d.name == file_info.name]:
#                     print(f'{file_info.name} есть в целевой папке')
#                     if file_info.hash != target_file.hash:
#                         print('Hash не совпадает!')
#                         print(
#                             f'Исходный:date={file_info.last_modified}, size={file_info.size} Целевой:{target_file.last_modified}, {target_file.size}')
#
#
#     def smart_copy(self, file_info):
#         """Умное копирование: заменяет целевой файл, если исходный больше или свежее."""
#         target_files = self.target.get_file(file_info.name)
#         if target_files:
#             for target_file in target_files:
#                 if (file_info.size > target_file.size) or (file_info.last_modified > target_file.last_modified):
#                     print(f"Копирование файла: {file_info.full_path} -> {target_file.full_path} (больше или свежее)")
#                     shutil.copy2(file_info.full_path, target_file.full_path)  # Копируем файл с сохранением метаданных
#                     file_info.path.unlink()
#                     self.deleted_files_count()
#                 else:
#                     print(f"Файл не заменен: {target_file.full_path} (целевой файл актуальнее)")
#                     file_info.path.unlink()
#                     self.deleted_files_count()
#
#     def _remove_empty_dirs(self, dir_path): #TODO Функцией удаления папок должен заниматься отдельный класс, а не внутри очистителя
#         """Удаляет пустые папки и увеличивает счетчик удаленных папок."""
#         # Перебираем все подкаталоги в директории
#         for subdir in dir_path.iterdir():
#             if subdir.is_dir():
#                 self._remove_empty_dirs(subdir)  # Рекурсивно проверяем подкаталоги
#
#                 # Если директория пустая, удаляем её
#                 if not any(subdir.iterdir()):
#                     print(f"Удаление пустой папки: {subdir}")
#                     subdir.rmdir()
#                     self.deleted_dirs_count()  # Увеличиваем счетчик удаленных папок






if __name__ == '__main__':
    # Испытание DirectoryInfo
    d = r'D:\!Science\Физтех\Циклирования\Разобрать эксперименты'
    # print(d)
    d = DirectoryIter(d)
    # s = r'D:\!Science\Физтех\Циклирования\Разобрать эксперименты'
    # # source = DirectoryInfo(s, '*')
    # # print(*[f for f in source.files if f.extension not in ['.xlsx', '.ndax']], sep='\n')
    # cleaner = DirectoryCleaner(s, d)
    # cleaner._remove_empty_dirs(cleaner.target.path)
    duplicates = dict()
    for first, second in combinations(d, 2):
        if first.hash == second.hash:
            if first.hash in duplicates:
                duplicates[first.hash].update([first, second])
            else:
                duplicates[first.hash] = {first, second}
    print(duplicates)
    # for value in duplicates.values():
    #     for file in list(value)[1:]:
    #         file.delete()
    pass
