import sys

from mus2muc.interfaces import MUS, CertifierOutput
from mus2muc.utils import Logger


class MUCWriter:
    def __init__(self, output_file, mapping):
        super().__init__()
        self.output_file = output_file
        self.mapping = mapping
        self.counter = Logger.start
        self.id = 0

    def __write__(self, something):
        if self.output_file is None:
            sys.stdout.write(something + "\n")
            sys.stdout.flush()

        else:
            with open(self.output_file, "a") as f:
                f.write(something + "\n")
                f.flush()

    def found_a_mus(self, mus: MUS):
        pass

    def mus_is_a_muc(self, mus: MUS, cert_out: CertifierOutput):
        pass

    def mus_is_a_false_positive(self, mus: MUS, cert_out: CertifierOutput):
        pass

    def mus_is_skipped(self, mus: MUS):
        pass

    def found_empty_mus(self, mus: MUS):
        pass

    def generator_restart(self, k: int):
        pass
