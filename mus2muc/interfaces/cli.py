from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Optional


class CertifierType(StrEnum):
    BLACK = "black"
    AALTAF = "aaltaf"


@dataclass(frozen=True)
class Options:
    input_formula: Path
    keep_probe: bool
    probe_path: Path
    k_start: int
    certifier_type: CertifierType
    output_file: Path
    total_timeout: Optional[int]
    total_mucs: Optional[int]
    bin_folder: Path
    verbose: bool

    def __post_init__(self):
        if self.total_mucs is not None and self.total_mucs <= 0:
            raise RuntimeError("Total number of MUCs should be a positive integer.")

        if self.total_timeout is not None and self.total_timeout <= 0:
            raise RuntimeError(
                "Total allowed runtime must be a positive integer (seconds)."
            )

        if not Path(self.input_formula).is_file():
            raise FileNotFoundError(self.input_formula)

        if self.k_start <= 0:
            raise ValueError("Starting value for k must be greater than zero")
