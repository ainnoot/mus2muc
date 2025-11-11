from abc import ABC, abstractmethod
from typing import Generator, Sequence
from mus2muc.interfaces import MUS


class MUSGenerator(ABC):
    def __init__(self, start_horizon: int) -> None:
        self.horizon: int = start_horizon

    @abstractmethod
    def set_horizon_and_restart(self, h: int) -> None:
        self.horizon = h

    @abstractmethod
    def get_muses(self) -> Sequence[MUS]:
        pass

    def start(self):
        pass

    def kill(self):
        pass
