import os
import re
import sys
import logging
import typing
from collections import namedtuple
from pathlib import Path

from utils import (
    BaseParsingException,
    ValidationError,
    exists,
    absolute,
    isempty,
    isdir,
    isfile,
    touch,
    rm,
)

Option = namedtuple("option", ["filename", "outdir", "delimiter", "indent"])


def main():
    filename = sys.argv[1]
    FileParser(logger_level=logging.DEBUG).parse(filename)


class FileParser:
    def __init__(self, logger_level=logging.INFO):
        self._logger = logging.getLogger(self.name)
        self._logger_level = logger_level
        self._config_logger()
        self._previous_position = 0
        self._current_dir = None
        self._base_dir = None
        self._line_number = None

    def parse(
        self,
        filename: typing.Union[str, Path],
        outdir: typing.Union[str, Path] = ".",
        delimiter: str = "/",
        indent: str = "\t",
    ):
        """
        filename: The path to file to parse.
        outdir: The output directory [default = .]
        delimiter: The folder marker sign [default = /]
        indent: The indentation marker sign [default = \t]
        """
        options = {
            "filename": filename,
            "outdir": outdir,
            "delimiter": delimiter,
            "indent": indent,
        }

        try:
            options = self._validate(options)
        except ValidationError as e:
            self.logger.error(e.detail)
            return

        filename, outdir, delimiter, indent = options

        self._parse(
            filename=filename, outdir=outdir, delimiter=delimiter, indent=indent
        )

    def _parse(self, filename: Path, outdir: Path, delimiter: str, indent: str):
        with open(filename, "r") as f:
            self._logger.info("Starting ...")
            root = next(f).strip("\n")
            if not isdir(root, delimiter=delimiter):
                self._logger.error("The root of the hierarchy must be a folder.")
                return

            base_dir = self._create_base_dir(outdir, root)

            if not base_dir:
                return

            self._line_number = 1
            self._current_dir = base_dir

            for line in f:
                self._line_number += 1
                line = line.strip("\n")
                parent_dir = self._compute_parent_dir(line, indent)

                if not parent_dir:
                    continue

                try:
                    parent_dir = parent_dir / self._clean_line(line, delimiter, indent)

                    if isfile(line):
                        touch(parent_dir)

                    if isdir(line):
                        parent_dir.mkdir()
                        self._current_dir = parent_dir
                        self._previous_position += 1
                except OSError:
                    # We think it is better to continue and notice the user of some errors
                    # than suspend the generation process.
                    self._logger.warning(f"Cannot create file {parent_dir.as_posix()}.")

            self._logger.info("Process finished!")

    def _create_base_dir(
        self, outdir: typing.Union[str, Path], root: typing.Union[str, Path]
    ):
        root = (
            root
            if isinstance(root, Path) and root.is_absolute()
            else absolute(Path(root))
        )
        outdir = (
            outdir
            if isinstance(root, Path) and outdir.is_absolute()
            else absolute(Path(outdir))
        )

        if root != outdir and root.parent != outdir:
            self._logger.warning(
                "The root directory have to be child of outdir. outdir is took as fallback."
            )
            root = outdir

        # prevent in case outdir == root to have outdir/root
        # In this case we just take root as outdir.
        self._base_dir = outdir if outdir == root else root

        if exists(self._base_dir):
            print(
                f"The folder {self._base_dir.as_posix()} already exists. Do want to override it ? (yes/no): ",
                end="",
            )

            awnser = input().strip().lower()

            if awnser.startswith("y"):
                try:
                    rm(self._base_dir)
                except OSError:
                    self._logger.error(f"Cannot remove {self._base_dir.as_posix()}")
                    return
            else:
                return

        self._base_dir.mkdir()
        return self._base_dir

    def _compute_parent_dir(self, line: str, indent: str):
        pos = self._compute_cursor_position(line, indent)

        # The we can't step up we step more than one.
        # We just log and ignore such lines.
        if pos - self._previous_position > 1:
            self._logger.warning(
                f"Line {self._line_number} is ignored, wrong formatted line."
            )
            return

        # The previous position is greater than the current one
        # then we have to step back
        while self._previous_position - pos >= 0:
            self._current_dir = self._current_dir.parent
            self._previous_position -= 1

        return self._current_dir

    def _validate(self, data: typing.Dict):
        filename = data["filename"]
        outdir = data["outdir"]
        delimiter = data["delimiter"]
        indent = data["indent"]

        filename = self._validate_filename(filename)
        outdir = self._validate_outdir(outdir)

        return Option(
            filename=filename, outdir=outdir, delimiter=delimiter, indent=indent
        )

    def _validate_filename(self, filename: typing.Union[str, Path]) -> Path:
        filename = filename if isinstance(filename, Path) else Path(filename)
        filename = absolute(filename)

        if (
            not filename.is_file()
            or not exists(filename)
            or not os.access(filename, os.R_OK)
        ):
            raise ValidationError(detail="The file doesn't exist or is not readable.")

        return filename

    def _clean_line(self, line: str, delimiter: str, indent: str) -> str:
        return line.lstrip(indent).rstrip(delimiter)

    def _validate_outdir(self, outdir: typing.Union[str, Path]) -> Path:
        outdir = outdir if isinstance(outdir, Path) else Path(outdir)
        outdir = absolute(outdir)

        if not outdir.is_dir() or not exists(outdir) or not os.access(outdir, os.W_OK):
            raise ValidationError(detail="The folder doesn't exist or is not writable.")

        return outdir

    def _compute_cursor_position(self, line: str, indent: str) -> int:
        match = re.match(r"[" + indent + "]" + "*", line)
        return match.span()[1] if match else self._previous_position

    def _config_logger(self):
        c_handler = logging.StreamHandler()
        c_formatter = logging.Formatter("%(name)s [%(levelname)s] - %(message)s")
        c_handler.setLevel(self._logger_level)
        c_handler.setFormatter(c_formatter)
        self._logger.addHandler(c_handler)

    @property
    def name(self):
        return self.__class__.__name__


if __name__ == "__main__":
    main()
