from pathlib import Path


def isfile(path: str, del="/") -> bool:
    return not path.endswith(f"{del}")

def isdir(path: str, del="/") -> bool:
    return path.endswith(f"{del}")

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

