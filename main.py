import logging
import typing
from collections import namedtuple

from .utils import BaseParsingException, ValidationError, exists, absolute, isempty

Option = namedtuple("option", ["filename", "outdir", "delimiter", "indent"])


def main():
    FileParser(logger_level=logging.DEBUG).parse()


class FileParser:
    def __init__(self, logger_level=logging.INFO):
        self._logger = logging.getLogger(self.name)
        self._logger_level = logger_level
        self._config_logger()
        self._cursor_position = 1
        self._current_dir = None
        self._base_dir = None
        self._line_number

    def parse(
        filename: typing.Union[str, Path],
        outdir: typing.Union[str, Path] = None,
        delimiter: str = None,
        indent: str = None,
    ):
        """
        filename: The path to file to parse.
        outdir: The output directory [default = .]
        delimiter: The folder marker sign [default = /]
        indent: The indentation marker sign [default = \t]
        """
        options = Option(
            filename=filename, outdir=outdir, delimiter=delimiter, indent=indent
        )
        try:
            options = self._validate(options)
        except ValidationError as e:
            self.logger.error(e.detail)
            return

        filename, outdir, delimiter, indent = options

        self._parse(
            filename=filename, outdir=outdir, delimiter=delimiter, indent=indent
        )

    def _parse(filename: Path, outdir: Path, delimiter: str, indent: str):
        with open(filename, "r") as f:
            self._logger.info("Starting ...")
            hierarchy = f.read()
            root = next(hierarchy)

            if not isdir(root, delimiter=delimiter):
                self._logger.error("The root of hierarchy must be a folder.")
                return

            self._base_dir = self._compute_base_dir(outdir, root)
            self._base_dir.mkdir()

            self._line_number = 1
            self._current_dir = self._base_dir

            for line in hierarchy:
                self._line_number += 1
                parent_dir = self._compute_parent_dir(line, indent)
                if not parent_dir:
                    continue

                if isfile(line):
                    touch(self.parent_dir / line)

                if isdir(line):
                    (self.parent_dir / line).mkdir()

    def _compute_base_dir(outdir: Path, root: Path):
        root = root if root.is_absolute() else absolute(root)
        outdir = outdir if outdir.is_absolute() else absolute(outdir)
        return outdir if outdir == root else outdir

    def _compute_parent_dir(line: str, indent: str):
        pos = self._compute_cursor_position(line, indent)
        # ignore files that are more step greater than the previous
        # since the are malformed.
        if pos - self._cursor_position > 1:
            self._logger.warning(f"{self._line_number} is ignored.")
            return

        while pos <= self._cursor_position:
            self._current_dir = self._current_dir.parent
            pos += 1

        self._cursor_position = pos

        return self._current_dir

    def _validate(self, data: Option):
        filename = data.get("filename")
        outdir = data.get("outdir", ".")
        delimiter = data.get("delimiter", "/")
        indent = data.get("indent", "\t")

        filename = self._validate_filename(filename)
        outdir = self._validate_outdir(outdir)

        return Option(
            filename=filename, outdir=outdir, delimiter=delimiter, indent=indent
        )

    def _validate_filename(filename: typing.Union[str, Path]) -> Path:
        filename = filename if isinstance(filename, Path) else Path(filename)
        filename = absolute(filename)

        if (
            not filename.is_file()
            or not exists(filename)
            or not os.access(filename, os.R_OK)
        ):
            raise ValidationError(detail="The file doesn't exist or is not readable.")

        return filename

    def _validate_outdir(outdir: typing.Union[str, Path]) -> Path:
        outdir = outdir if isinstance(outdir, Path) else Path(outdir)
        outdir = absolute(outdir)

        if not outdir.is_dir() or not exists(outdir) or not os.access(outdir, os.W_OK):
            raise ValidationError(detail="The folder doesn't exist or is not writable.")

        return outdir

    def _compute_cursor_position(line: str, indent: str) -> int:
        match = re.match(r"[" + indent + "]" + "*")
        return match.span()[1] if match else self._cursor_position

    def _config_logger(self):
        c_handler = logging.StreamHandler()
        c_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        c_handler.setLevel(self.logger_level)
        c_handler.addFormatter(c_formatter)
        self._logger.addHandler(c_handler)

    @classmethod
    @property
    def name(self):
        return self.__class__.__name__


if __name__ == "__main__":
    main()
