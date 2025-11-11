from abc import ABC, abstractmethod
from time import perf_counter
from typing import Tuple, Optional
from mus2muc.interfaces import ConjunctMapping, MUCStatus, MUS, CertifierOutput
from mus2muc.utils import Logger


class Certifier(ABC):
    def __init__(self, mapping: ConjunctMapping):
        self.mapping = mapping

    @abstractmethod
    def __call_solver__(self, formula_string: str) -> Tuple[str, str]:
        pass

    @abstractmethod
    def __decode_solver_output__(
        self, stdout: str, stderr: str
    ) -> Tuple[MUCStatus, Optional[int]]:
        pass

    def __build_formula__(self, mus: MUS):
        return self.mapping.formula_given_indices(mus.objective_atoms)

    def certify(self, mus: MUS) -> CertifierOutput:
        formula = self.__build_formula__(mus)
        start = perf_counter()
        stdout, stderr = self.__call_solver__(formula)
        end = perf_counter()
        status, model_length = self.__decode_solver_output__(stdout, stderr)

        if status == MUCStatus.SATISFIABLE:
            assert model_length is not None

        return CertifierOutput(perf_counter() - Logger.start, end - start, model_length, status)
