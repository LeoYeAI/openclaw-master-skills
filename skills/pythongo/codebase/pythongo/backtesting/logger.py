import logging


class Logger(logging.Logger):
    def __init__(self, name: str, level: int | str = 0) -> None:
        super().__init__(name, level)
        
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)

        self.ch.setFormatter(logging.Formatter(
            fmt="[%(asctime)s] - %(levelname)-5s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        )

        self.addHandler(self.ch)

    def setLevel(self, level: int | str) -> None:
        self.ch.setLevel(level)
        return super().setLevel(level)


logger = Logger("PythonGO.BackTest")
