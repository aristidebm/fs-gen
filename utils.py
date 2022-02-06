from pathlib import Path
import shutil


class BaseParsingException(Exception):
    # Each subclass must provide a custom default_detail.
    default_detail = "An error has been occurred."

    def __init__(self, detail=None):
        self._detail = detail or self.default_detail

    def __str__(self):
        return self._detail


class ValidationError(BaseParsingException):
    default_detail = "Invalid data."


def isfile(path: str, delimiter="/") -> bool:
    return not path.endswith(f"{delimiter}")


def isdir(path: str, delimiter="/") -> bool:
    return path.endswith(f"{delimiter}")


def exists(path: Path) -> bool:
    return path.exists()


def absolute(path: Path) -> None:
    return path.absolute()


def islink(path: Path) -> bool:
    pass


def isempty(path: Path) -> bool:
    if not path.is_file():
        return True
    return bool(next(path.iterdir()))


def rm(filename: Path) -> None:
    if filename.is_dir():
        # Path.rmdir requires an empty folder
        # that is not what we want in our case.
        shutil.rmtree(filename)
        return
    filename.unlink()


def touch(path: Path) -> None:
    path.touch()
