import logging


def main():
    pass


class FileParser:
    def __init__(self, logger_level=logging.INFO):
        # FIXME: convert name to snake_case with python stdlib.
        self._logger = logging.getLogger(self.name)
        self._logger_level = logger_level
        self._config_logger()

    @property
    def logger(self):
        return self._logger

    @property
    def logger_level(self):
        return self._logger_level

    def parse():
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
