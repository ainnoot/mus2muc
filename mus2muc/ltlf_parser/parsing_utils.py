from pathlib import Path
from mus2muc.ltlf_parser import parse_formulae_and_annotate
from typing import Sequence


def compose_logic_program(formula_string: str, encoding: Path, target_file: Path):
    with target_file.open("w") as f:
        f.write(encoding.open("r").read() + "\n")

    parse_formulae_and_annotate(formula_string, target_file, "a")
    return target_file
