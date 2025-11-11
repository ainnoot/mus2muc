import json
from mus2muc.interfaces import MUS, CertifierOutput, MUCWriter


class OutputWriter(MUCWriter):
    def __init__(self, output_file, mapping):
        super().__init__(output_file, mapping)

    def found_a_mus(self, mus: MUS):
        pass

    def mus_is_a_muc(self, mus: MUS, cert_out: CertifierOutput):
        formula = self.mapping.formula_given_indices(mus.objective_atoms)
        output = {
            "id": self.id,
            "conjuncts": mus.objective_atoms,
            "size": mus.size,
            "formula": formula,
            "k": mus.k,
            "mus-compute-time": mus.mus_compute_time,
            "core-compute-time": cert_out.core_computation_time,
            "timestamps": {"mus": mus.timestamp, "certified": cert_out.timestamp},
        }
        self.id += 1

        self.__write__(json.dumps(output))

    def mus_is_a_false_positive(self, mus: MUS, cert_out: CertifierOutput):
        pass

    def mus_is_skipped(self, mus: MUS):
        pass

    def found_empty_mus(self, mus: MUS):
        pass

    def generator_restart(self, k: int):
        pass
