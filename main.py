import logging
import typing
from collections import namedtuple

from .utils import BaseParsingException, ValidationError, exists, absolute, isempty

Option = namedtuple("option", ["filename", "outdir", "delimiter", "indent"])


def main():
    pass


class FileParser:
    def __init__(self, logger_level=logging.INFO):
        # FIXME: convert name to snake_case with python stdlib.
        self._logger = logging.getLogger(self.name)
        self._logger_level = logger_level
        self._config_logger()
        # The position of the cursor.
        self._cursor = 1

    @property
    def logger(self):
        return self._logger

    @property
    def logger_level(self):
        return self._logger_level

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
            self.logger.error(e)
            return

        filename, outdir, delimiter, indent = options

        self._parse(
            filename=filename, outdir=outdir, delimiter=delimiter, indent=indent
        )

    def _parse(filename, outdir, delimiter, indent):
        pass

    def _validate(self, data: Option):
        filename = data.get("filename")
        outdir = data.get("outdir")
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

    def _get_indentation_level(line: str, indent: str) -> int:
        pass

    def _config_logger(self):
        c_handler = logging.StreamHandler()
        c_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        c_handler.setLevel(self.logger_level)
        c_handler.addFormatter(c_formatter)
        self.logger.addHandler(c_handler)

    @classmethod
    @property
    def name(self):
        return self.__class__.__name__


if __name__ == "__main__":
    main()
