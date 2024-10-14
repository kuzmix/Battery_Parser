import hashlib
import shutil
from datetime import datetime
from pathlib import Path


class FileInfo:
    """
    Создаёт файл и сохраняет информацию о нём.


    """

    def __init__(self, file_path: str, ):
        self.path = Path(file_path)
        if not self.path.is_file():
            raise ValueError(f"'{file_path}' не является файлом.")

    @property
    def name(self):
        """Возвращает имя файла."""
        return self.path.name

    @property
    def extension(self):
        """Возвращает расширение файла."""
        return self.path.suffix

    @property
    def full_path(self):
        """Возвращает полный путь файла."""
        return str(self.path.resolve())

    @property
    def dir(self):
        return self.path.parent

    @property
    def size(self):
        """Возвращает размер файла в байтах."""
        return self.path.stat().st_size

    @property
    def last_modified(self):
        """Возвращает дату последней модификации файла."""
        timestamp = self.path.stat().st_mtime
        return datetime.fromtimestamp(timestamp)

    def compute_hash(self, algorithm: str = 'sha256', chunk_size: int = 1024):
        """Вычисляет хэш файла (по умолчанию SHA-256)."""
        if algorithm not in hashlib.algorithms_available:
            raise ValueError('')
        hash_func = hashlib.new(algorithm)
        with open(self.path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @property
    def hash(self):
        """Возвращает хэш файла (по умолчанию SHA-256)."""
        return self.compute_hash()

    def __repr__(self):
        return f"<FileInfo(name={self.name} , path={self.dir}, size={self.size / (1024) ** 2:.4}MB>"


class DirectoryInfo:
    """
    Класс для управления директорией из файлов
    При обращении по индексу выводит список файлов в подпапке, которая передана в роли индекса
    """

    def __init__(self, dir_path):
        self.path = Path(dir_path).resolve()
        if not self.path.is_dir():
            raise ValueError(f"'{dir_path}' не является директорией.")

        self.files = self._get_files()
        self.hashes = self._get_hashes()

    def _get_hashes(self):
        return {f.hash:f.name for f in self.files}

    def get_file(self, file_name):
        """Возвращает объект FileInfo или список объектов для имени файла"""
        files = []
        for file_info in self.files:
            if file_info.name == file_name:
                files.append(file_info)
        return files if files else None

    def _get_files(self):
        """Получает все файлы в директории, включая поддиректории."""
        return [FileInfo(f) for f in self.path.rglob('*') if f.is_file()]

    def __getitem__(self, relative_path):
        """Возвращает объект FileInfo для файла по относительному пути."""
        absolute_path = self.path / relative_path
        return [f for f in self.files if str(absolute_path) in str(f.dir)]

    def update(self):
        self.files = self._get_files()
        self.hashes = self._get_hashes()

    def __repr__(self):
        return f"<DirectoryInfo(path={self.path}, files={len(self.files)})>"


class DirectoryCleaner:
    """
    Удаляет ненужные файлы
    """

    def __init__(self, source_dir: (str, DirectoryInfo), target_dir: (str, DirectoryInfo)):
        self.source = self._handle_path(source_dir)
        self.target = self._handle_path(target_dir)
        self.deleted_files_count = 0  # Счетчик удаленных файлов
        self.deleted_dirs_count = 0  # Счетчик удаленных папок

    def clean(self, smart_copy=True):
        """Удаляет файлы из исходной директории, если они уже существуют в целевой директории."""
        for file_info in self.source.files:
            if file_info.hash in self.target.hashes:
                str_output = f"Удаление файла: {file_info.name} (существует в целевой директории)"
                if self.target.hashes[file_info.hash] == file_info.name:
                    str_output += ' + совпадает с целевым по имени+'
                print(str_output)
                file_info.path.unlink()  # Удаление файла
                self.deleted_files_count += 1  # Увеличиваем счетчик удаленных файлов
            else:
                if smart_copy:
                    self.smart_copy(file_info)
        self.target.update()
        self.source.update()
        # Удаляем пустые папки из исходной директории
        self._remove_empty_dirs(self.source.path)

        # Выводим количество удаленных файлов и папок
        print(f"\nУдалено файлов: {self.deleted_files_count}")
        print(f"Удалено папок: {self.deleted_dirs_count}")

    def check_filenames(self):
        """
        Checks if
        Returns:
            None

        """
        target_names = [f.name for f in self.target.files]
        for file_info in self.source.files:
            if file_info.name in target_names:
                if len([d for d in self.target.files if d.name == file_info.name]) > 1:
                    print(f"Более одного совпадающего файла для {file_info.name}")
                for target_file in [d for d in self.target.files if d.name == file_info.name]:
                    print(f'{file_info.name} есть в целевой папке')
                    if file_info.hash != target_file.hash:
                        print('Hash не совпадает!')
                        print(
                            f'Исходный:date={file_info.last_modified}, size={file_info.size} Целевой:{target_file.last_modified}, {target_file.size}')

    @staticmethod
    def _handle_path(path_dir):
        if not isinstance(path_dir, DirectoryInfo):
            return DirectoryInfo(path_dir)
        else:
            return path_dir

    def smart_copy(self, file_info):
        """Умное копирование: заменяет целевой файл, если исходный больше или свежее."""
        target_files = self.target.get_file(file_info.name)
        if target_files:
            for target_file in target_files:
                if (file_info.size > target_file.size) or (file_info.last_modified > target_file.last_modified):
                    print(f"Копирование файла: {file_info.full_path} -> {target_file.full_path} (больше или свежее)")
                    shutil.copy2(file_info.full_path, target_file.full_path)  # Копируем файл с сохранением метаданных
                    file_info.path.unlink()
                    self.deleted_files_count += 1
                else:
                    print(f"Файл не заменен: {target_file.full_path} (целевой файл актуальнее)")
                    file_info.path.unlink()
                    self.deleted_files_count += 1

    def _remove_empty_dirs(self, dir_path):
        """Удаляет пустые папки и увеличивает счетчик удаленных папок."""
        # Перебираем все подкаталоги в директории
        for subdir in dir_path.iterdir():
            if subdir.is_dir():
                self._remove_empty_dirs(subdir)  # Рекурсивно проверяем подкаталоги

                # Если директория пустая, удаляем её
                if not any(subdir.iterdir()):
                    print(f"Удаление пустой папки: {subdir}")
                    subdir.rmdir()
                    self.deleted_dirs_count += 1  # Увеличиваем счетчик удаленных папок


if __name__ == '__main__':
    # Испытание DirectoryInfo
    d = DirectoryInfo(r'D:\!Science\Физтех\Циклирования\Эксперименты_метро')
    print(d)
    s = DirectoryInfo(r'D:\!Science\Физтех\Циклирования\Разобрать эксперименты')
    print(s)
    cleaner = DirectoryCleaner(s, d)
    cleaner.clean(smart_copy=True)
    print(s, d)
    # cleaner.check_filenames()
    # print(d.get_file('BTS82-133-1-8-95-20240415102037-4.2.ndax'))
