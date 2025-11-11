import json
from time import perf_counter

from mus2muc.interfaces import MUS, CertifierOutput, MUCWriter
from mus2muc.utils import Logger


class VerboseWriter(MUCWriter):
    def __init__(self, output_file, mapping):
        super().__init__(output_file, mapping)

    def found_a_mus(self, mus: MUS):
        formula = self.mapping.formula_given_indices(mus.objective_atoms)
        output = {
            "event": "FOUND_MUS",
            "objective_atoms": mus.objective_atoms,
            "size": mus.size,
            "k": mus.k,
            "formula": formula,
            "mus-compute-time": mus.mus_compute_time,
            "timestamps": {"mus": mus.timestamp},
        }
        self.__write__(json.dumps(output))

    def mus_is_a_false_positive(self, mus: MUS, cert_out: CertifierOutput):
        output = {
            "event": "NOT_A_MUC",
            "objective_atoms": mus.objective_atoms,
            "size": mus.size,
            "k": mus.k,
            "model_length": cert_out.witness_model_length,
            "mus-compute-time": mus.mus_compute_time,
            "core-compute-time": cert_out.core_computation_time,
            "timestamps": {"mus": mus.timestamp, "cert": cert_out.timestamp},
        }
        self.__write__(json.dumps(output))

    def mus_is_a_muc(self, mus: MUS, cert_out: CertifierOutput):
        formula = self.mapping.formula_given_indices(mus.objective_atoms)
        output = {
            "event": "FOUND_MUC",
            "id": self.id,
            "objective_atoms": mus.objective_atoms,
            "size": mus.size,
            "formula": formula,
            "k": mus.k,
            "mus-compute-time": mus.mus_compute_time,
            "core-compute-time": cert_out.core_computation_time,
            "timestamps": {"mus": mus.timestamp, "certified": cert_out.timestamp},
        }
        self.id += 1
        self.__write__(json.dumps(output))

    def mus_is_skipped(self, mus: MUS):
        output = {
            "event": "SKIP_MUS",
            "objective_atoms": mus.objective_atoms,
            "size": mus.size,
            "k": mus.k,
            "mus-compute-time": mus.mus_compute_time,
            "timestamps": {"mus": mus.timestamp},
        }
        self.__write__(json.dumps(output))

    def found_empty_mus(self, mus: MUS):
        output = {
            "event": "EMPTY_MUS",
            "objective_atoms": mus.objective_atoms,
            "size": mus.size,
            "k": mus.k,
            "mus-compute-time": mus.mus_compute_time,
            "timestamps": {"mus": mus.timestamp},
        }
        self.__write__(json.dumps(output))

    def generator_restart(self, k):
        output = {
            "event": "GENERATOR_RESTART",
            "k": k,
            "timestamps": {"restart": perf_counter() - Logger.start},
        }
        self.__write__(json.dumps(output))
