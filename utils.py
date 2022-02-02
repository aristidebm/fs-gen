from pathlib import Path


class BaseParsingException(Exception):
    pass


def isfile(path: str, delimiter="/") -> bool:
    return not path.endswith(f"{delimiter}")


def isdir(path: str, delimiter="/") -> bool:
    return path.endswith(f"{delimiter}")


def exists(path: Path) -> bool:
    return path.exists()


def islink(path: str) -> bool:
    pass


def rm(filename: Path) -> None:
    # FIXME: find the diff between this and shutil.rmtree
    if filename.is_dir():
        Path.rmdir(filename)
        return
    filename.unlink()


def touch(path: Path) -> None:
    path.touch()
