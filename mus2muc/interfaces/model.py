from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Tuple, Optional, Dict


@dataclass(frozen=True)
class ConjunctMapping:
    mapping: Dict[str, str]

    @staticmethod
    def from_formula_string(formula_string):
        formula_dict = dict()
        for line in formula_string.splitlines():
            line = line.strip()
            fid, f = line.split(":=")
            formula_dict[fid.strip()] = f.strip()[:-1]
        return ConjunctMapping(formula_dict)

    def formula_given_indices(self, indices: Tuple[str, ...]) -> str:
        return " & ".join("(" + self.mapping[i] + ")" for i in indices)


@dataclass(frozen=True)
class MUS:
    k: int
    objective_atoms: Tuple[str, ...]
    timestamp: float
    mus_compute_time: float

    @property
    def size(self):
        return len(self.objective_atoms)

    @property
    def empty(self):
        return len(self.objective_atoms) == 0


@dataclass(frozen=True)
class CertifierOutput:
    timestamp: float
    core_computation_time: float
    witness_model_length: Optional[int]
    result: "MUCStatus"

    @property
    def unknown(self):
        return self.result == MUCStatus.UNKNOWN

    @property
    def satisfiable(self):
        return self.result == MUCStatus.SATISFIABLE

    @property
    def unsatisfiable(self):
        return self.result == MUCStatus.UNSATISFIABLE


class MUCStatus(IntEnum):
    UNKNOWN = auto()
    SATISFIABLE = auto()
    UNSATISFIABLE = auto()
