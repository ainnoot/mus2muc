from mus2muc.certifiers.aaltaf import AALTAFCertifier
from mus2muc.certifiers.black import BLACKCertifier
from mus2muc.generators import WASPGenerator, WASPGeneratorThread
from mus2muc.interfaces import ConjunctMapping, Options, CertifierType
from mus2muc.ltlf_parser import compose_logic_program
import sys
from mus2muc.enumeration import MUS2MUC
from argparse import ArgumentParser
from mus2muc.enumeration import LTLF2ASP_ENCODING_PATH
from mus2muc.utils import Logger
from pathlib import Path
import os
from time import perf_counter

from mus2muc.writers import OutputWriter, VerboseWriter


def check_dependencies(certifier, bin_folder):
    files = [x.name for x in bin_folder.glob("*")]
    fail = False
    if "wasp" not in files:
        fail = True
        print("Missing MUS generator dependency: wasp")

    if certifier.name.lower() not in files:
        fail = True
        print("Missing LTLf certifier dependency:", certifier.name)

    if fail:
        print("Please check out installation instruction.")
        sys.exit(118)


def parse_args() -> Options:
    parser = ArgumentParser(prog="mus2muc")
    parser.add_argument(
        "formula", type=Path, help="Path to a formula in .ltlfconj format."
    )

    parser.add_argument(
        "--min-k",
        "-k",
        type=int,
        help="Starting value for MUC horizon search.",
        default=1,
    )
    parser.add_argument(
        "--probe-path",
        type=Path,
        help="Path to store the logic program used as a probe.",
    )
    parser.add_argument("--keep-probe", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--certifier",
        "-c",
        type=CertifierType,
        choices=[CertifierType.BLACK, CertifierType.AALTAF],
        default=CertifierType.AALTAF,
    )
    parser.add_argument("--output", "-o", type=Path, default=None)
    parser.add_argument("-t", "--total-timeout", type=int, default=None)
    parser.add_argument("-n", "--total-mucs", type=int, default=None)
    parser.add_argument(
        "--bin-folder",
        type=Path,
        help="Path to certifier executables.",
        default="/usr/bin",
    )

    args = parser.parse_args()

    return Options(
        input_formula=args.formula,
        keep_probe=args.keep_probe,
        probe_path=args.probe_path,
        k_start=args.min_k,
        certifier_type=args.certifier,
        output_file=args.output,
        total_mucs=args.total_mucs,
        total_timeout=args.total_timeout,
        bin_folder=args.bin_folder.resolve(),
        verbose=args.verbose,
    )


def get_certifier_by_type(t):
    if t == CertifierType.BLACK:
        return BLACKCertifier
    if t == CertifierType.AALTAF:
        return AALTAFCertifier


def main():
    options = parse_args()
    check_dependencies(options.certifier_type, options.bin_folder)

    Logger.log(options.__dict__)

    probe_file = (
        options.input_formula.with_name(
            f".instance={options.input_formula.name}_{os.getpid()}_{perf_counter()}_probe.lp"
        )
        if options.probe_path is None
        else options.probe_path
    )

    formula_string = options.input_formula.open("r").read()
    m = ConjunctMapping.from_formula_string(formula_string)
    prg = compose_logic_program(formula_string, LTLF2ASP_ENCODING_PATH, probe_file)

    certifier_cls = get_certifier_by_type(options.certifier_type)
    certifier = certifier_cls(m, options.bin_folder / certifier_cls.EXECUTABLE_NAME)
    generator = WASPGeneratorThread(options.k_start, prg, options.bin_folder)
    writer = (
        VerboseWriter(options.output_file, m)
        if options.verbose
        else OutputWriter(options.output_file, m)
    )

    solver = MUS2MUC(generator, certifier, writer, options)
    exit_code = solver.start()

    Logger.log("Complete, exit code: {}".format(exit_code))

    if options.keep_probe is False:
        probe_file.unlink()

    sys.exit(exit_code)
