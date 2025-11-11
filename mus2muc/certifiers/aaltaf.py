from mus2muc.interfaces import Certifier, ConjunctMapping, MUCStatus
from subprocess import Popen, PIPE
from typing import Tuple, Optional
from mus2muc.constants import Constants
import tempfile

class AALTAFCertifier(Certifier):
    EXECUTABLE_NAME = "aaltaf"

    def __init__(self, m: ConjunctMapping, aaltaf_executable_name):
        self.executable_name = aaltaf_executable_name
        super().__init__(m)

    def __call_solver__(self, formula_string: str) -> Tuple[str, str]:
        cmd = [self.executable_name, "-e"]
        with tempfile.TemporaryDirectory() as tempdir:
            aaltaf_process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=tempdir)
            try:
                aaltaf_stdout, aaltaf_stderr = aaltaf_process.communicate(
                    formula_string.encode("ascii")
                )

                return aaltaf_stdout.decode("ascii"), aaltaf_stderr.decode("ascii")

            finally:
                aaltaf_process.kill()

    def __decode_solver_output__(
        self, stdout: str, stderr: str
    ) -> Tuple[MUCStatus, Optional[int]]:
        if len(stderr) > 0:
            raise RuntimeError("Qualcosa non va in AALTAF", stderr)

        aaltaf_ans = stdout.splitlines()

        assert aaltaf_ans[0].strip() == "please input the formula:"

        aaltaf_result = aaltaf_ans[1].strip()
        if aaltaf_result == Constants.AALTAF_UNSAT:
            return MUCStatus.UNSATISFIABLE, None
        elif aaltaf_result == Constants.AALTAF_SAT:
            return MUCStatus.SATISFIABLE, len(aaltaf_ans[2:])

        return MUCStatus.UNKNOWN, None
