import sys
from time import perf_counter
from typing import Optional
from mus2muc.interfaces import MUSGenerator
from mus2muc.constants import Constants
from pathlib import Path
from subprocess import Popen, PIPE
from clingo import parse_term
from mus2muc.interfaces import MUS
from mus2muc.utils import Logger
from multiprocessing import Process, JoinableQueue

class WaspRunner(Process):
    def __init__(self, k: int, logic_program_file_path: Path, bin_folder: Path):
        super().__init__()
        self.k = k
        self.filepath = logic_program_file_path
        self.bin_folder = bin_folder

        self.queue = JoinableQueue()
        self.horizon = k

    def run(self):
        gringo_cmd = [
            "gringo",
            "-o",
            "smodels",
            "-c",
            f"k={self.horizon}",
            self.filepath.as_posix(),
        ]

        wasp_cmd = [
            self.bin_folder / "wasp",
            f"--mus={Constants.MUS_PREDICATE_NAME}",
            "-n",
            "0",
        ]

        gringo = Popen(gringo_cmd, stdout=PIPE, stderr=PIPE)
        wasp = Popen(wasp_cmd, stdin=gringo.stdout, stderr=PIPE, stdout=PIPE)

        try:
            buffer = []
            for row, line in enumerate(wasp.stdout):
                line = line.strip().decode("ascii")
                mus = self.__parse_mus__(line)
                if mus is not None:
                    buffer.append(mus)

                if len(buffer) > 5:
                    self.queue.put(tuple(buffer))
                    buffer.clear()

            if len(buffer) > 0:
                self.queue.put(tuple(buffer))
                buffer.clear()

            self.queue.put(tuple())

        except Exception as e:
            wasp.terminate()

        finally:
            wasp.terminate()

    def __parse_mus__(self, wasp_line_output: str) -> Optional[MUS]:
        # TODO: Parsing the time-stamp
        if not wasp_line_output.startswith("[MUS #"):
            return None

        timestamp, atoms = wasp_line_output.split(': ')
        mus_atoms = [parse_term(x) for x in atoms.split(" ")]

        timestamp = int(timestamp.split('] ')[1])

        rbracket_idx = wasp_line_output.find("]")
        # [MUS #3] 53487: a b c x y z
        return MUS(
            self.horizon,
            tuple(x.arguments[0].string for x in mus_atoms),
            perf_counter() - Logger.start,
            timestamp / 1000
        )


class WASPGeneratorThread(MUSGenerator):
    def __init__(self, k: int, logic_program_file_path: Path, bin_folder):
        super().__init__(k)
        self.filepath = logic_program_file_path
        self.bin_folder = bin_folder
        self.k = k
        self.runner = WaspRunner(k, logic_program_file_path, bin_folder)

    def set_horizon_and_restart(self, k):
        self.kill()
        self.k = k
        self.runner = WaspRunner(self.k, self.filepath, self.bin_folder)
        self.start()

    def start(self):
        self.runner.start()

    def kill(self):
        self.runner.kill()

    def get_muses(self):
        mus_buffer = self.runner.queue.get()
        self.runner.queue.task_done()
        return mus_buffer
