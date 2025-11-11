import json
from mus2muc.interfaces import Certifier, ConjunctMapping, MUCStatus
from subprocess import Popen, PIPE
from typing import Tuple, Optional
from mus2muc.constants import Constants


class BLACKCertifier(Certifier):
    EXECUTABLE_NAME = "black"

    def __init__(self, m: ConjunctMapping, black_executable_name):
        self.executable_name = black_executable_name
        super().__init__(m)

    def __call_solver__(self, formula_string: str) -> Tuple[str, str]:
        cmd = [
            self.executable_name,
            "solve",
            "--finite",
            "--model",
            "-o",
            "json",
            "-",
        ]
        black_process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            stdout, stderr = black_process.communicate(formula_string.encode("ascii"))
            return stdout.decode("ascii"), stderr.decode("ascii")

        finally:
            black_process.kill()

    def __decode_solver_output__(
        self, stdout: str, stderr: str
    ) -> Tuple[MUCStatus, Optional[int]]:
        if len(stderr) > 0:
            raise RuntimeError("BLACK STDERR NOT EMPTY", stderr)

        black_ans = json.loads(stdout)
        black_result = black_ans["result"].strip()

        if black_result == Constants.BLACK_UNSAT:
            return MUCStatus.UNSATISFIABLE, None

        elif black_result == Constants.BLACK_SAT:
            return MUCStatus.SATISFIABLE, black_ans["model"]["size"]

        return MUCStatus.UNKNOWN, None
