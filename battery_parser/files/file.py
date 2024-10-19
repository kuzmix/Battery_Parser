import hashlib
import shutil
from datetime import datetime
from pathlib import Path


class FileInit:
    """
    Инициация файлов по их пути - начальный класс для работы с файлами. Создаётся по пути файла.
    """

    def __init__(self, file_path: str, ):
        self.path = Path(file_path)
        if not self.path.is_file():
            raise ValueError(f"'{file_path}' не является файлом.")


class FileInfo(FileInit):
    """
    Класс для получения информации о файле.
    """

    @property
    def name(self) -> str:
        """Возвращает название файла с расширением."""
        return self.path.name

    @property
    def extension(self) -> str:
        """- Возвращает расширение файла. """
        return self.path.suffix

    @property
    def full_path(self) -> Path:
        """Возвращает полный путь файла."""
        return self.path.resolve()

    @property
    def dir(self) -> Path:
        """Возвращает директорию файла"""
        return self.path.parent

    @property
    def size(self) -> int:
        """Возвращает размер файла в байтах."""
        return self.path.stat().st_size

    @property
    def last_modified(self) -> datetime:
        """Возвращает дату последней модификации файла."""
        timestamp = self.path.stat().st_mtime
        return datetime.fromtimestamp(timestamp)

    def __repr__(self):
        return f"<FileInfo(name={self.name} , path={str(self.dir)}, size={self.size / (1024) ** 2:.4}MB>"


class FileAction(FileInfo):
    """
    Класс позволяет проводить над файлами операции -
    """
    algorithm: str = 'sha256',
    chunk_size: int = 1024,
    def __init__(self, file_path: str,
                 root_dir: (Path, str) = None):
        super().__init__(file_path)
        self.root_dir = None if root_dir is None else Path(root_dir)
        self.hash = self._compute_hash()

    def copy(self, destination: Path):
        """Создаёт копию файла по переданному пути
            - Если передаётся путь на директорию - то скопировать файл туда с оригинальным именем
            - Если передаёт имя файла - копирует файл под это имя"""
        if destination.is_file():
            print(f'Копирование {self.path} перезаписывает {destination}.')
        shutil.copy2(self.path, destination)

    def move(self, destination: Path):
        """
        Перемещает файл по переданному пути

        :param destination: Путь, по котором происходит перемещение.
                - Если передаётся путь на директорию - то скопировать файл туда с оригинальным именем
                - Если передаёт имя файла - копирует файл под это имя
        :type destination: Path
        :return: None
        :rtype:
        """
        if destination.is_file():
            print(f'Перемещение {self.path} перезаписывает {destination}.')
        shutil.move(self.path, destination)

    def delete(self):
        """Удаляет данный файл"""
        self.path.unlink()

    def _compute_hash(self) -> str:
        """Вычисляет хэш файла (по умолчанию SHA-256)."""
        hash_func = hashlib.new(self.algorithm)
        with open(self.path, 'rb') as f:
            while chunk := f.read(self.chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm):
        if algorithm not in hashlib.algorithms_available:
            raise ValueError('Algorithm not supported.')
        self.__class__._algorithm = algorithm


class File(FileAction):
    pass
