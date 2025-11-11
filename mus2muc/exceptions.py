# TODO: Errori di WASP, di BLACK, tutte le cose che possono andare storte


class ParsingError(Exception):
    pass


class UnsupportedOperator(Exception):
    def __init__(self, string: str) -> None:
        self.string: str = string

    def message(self) -> str:
        return self.string
