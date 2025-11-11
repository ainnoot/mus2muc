from typing import Tuple
from mus2muc.interfaces import MUS


class MUSCache:
    def __init__(self):
        self.muses = set()

    def __get_objective_atoms__(self, mus: MUS) -> Tuple[str, ...]:
        return tuple(sorted(mus.objective_atoms))

    def __hash_mus__(self, mus: MUS) -> int:
        return hash(self.__get_objective_atoms__(mus))

    def contains(self, mus: MUS) -> bool:
        mus_hash = self.__hash_mus__(mus)
        return mus_hash in self.muses

    def add_if_not_contained(self, mus: MUS) -> bool:
        muc_hash = self.__hash_mus__(mus)
        if muc_hash in self.muses:
            return False

        self.muses.add(muc_hash)
        return True
