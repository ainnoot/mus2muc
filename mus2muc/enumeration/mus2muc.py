import time
from pathlib import Path

from mus2muc.interfaces import ConjunctMapping, Certifier, MUSGenerator
from mus2muc.generators import WASPGenerator, WASPGeneratorThread
from mus2muc.enumeration.mus_cache import MUSCache
from mus2muc.interfaces import Options, MUCWriter
from mus2muc.utils import log, Logger
import enum


class MUS2MUCResult(enum.IntEnum):
    FOUND_ALL_MUCS = 10
    TIMEOUT = 20
    FOUND_REQUIRED_MUCS = 30
    SOME_ERROR = 40
    RESTART = 50
    NEXT_BATCH = 60


class MUS2MUC:
    def __init__(
        self,
        generator: MUSGenerator,
        certifier: Certifier,
        writer: MUCWriter,
        options: Options,
    ):
        self.options = options
        self.certifier = certifier
        self.generator = generator
        self.writer = writer
        self.found_mucs = 0

    def timeout(self) -> bool:
        if self.options.total_timeout is None:
            return False

        elapsed = time.perf_counter() - Logger.start
        return elapsed > self.options.total_timeout

    def found_required_mucs(self):
        if self.options.total_mucs is None:
            return False

        return self.found_mucs >= self.options.total_mucs

    def start(self):
        return self.enumerate_muses()

    def __process_mus_batch__(self, mus_buffer, cache, k):
        for mus in mus_buffer:
            if mus.empty:
                log("Found the empty MUS, doubling horizon")
                self.generator.set_horizon_and_restart(k * 2)

                self.writer.found_empty_mus(mus)
                return MUS2MUCResult.RESTART

            if cache.contains(mus):
                self.writer.mus_is_skipped(mus)
                continue

            self.writer.found_a_mus(mus)
            certifier_result = self.certifier.certify(mus)

            if certifier_result.unknown:
                return MUS2MUCResult.SOME_ERROR

            elif certifier_result.satisfiable:
                self.writer.mus_is_a_false_positive(mus, certifier_result)
                assert certifier_result.witness_model_length is not None
                k = certifier_result.witness_model_length
                log(f"Expanding horizon to {k=}")
                self.generator.set_horizon_and_restart(k)

                return MUS2MUCResult.RESTART

            elif certifier_result.unsatisfiable:
                self.writer.mus_is_a_muc(mus, certifier_result)
                cache.add_if_not_contained(mus)
                self.found_mucs += 1

                if self.found_required_mucs():
                    log("Found required number of MUCs")
                    return MUS2MUCResult.FOUND_REQUIRED_MUCS

        return MUS2MUCResult.NEXT_BATCH

    def enumerate_muses(self):
        cache = MUSCache()
        k = self.options.k_start
        continue_search = True

        self.generator.start()

        while continue_search:
            continue_search = False

            self.writer.generator_restart(self.generator.horizon)
            while mus_buffer := self.generator.get_muses():
                if self.timeout():
                    log("Timeout reached!")
                    return MUS2MUCResult.TIMEOUT

                status = self.__process_mus_batch__(mus_buffer, cache, k)

                if status is MUS2MUCResult.NEXT_BATCH:
                    continue

                elif status is MUS2MUCResult.RESTART:
                    continue_search = True
                    break

                else:
                    return status


        self.generator.kill()
        return MUS2MUCResult.FOUND_ALL_MUCS
