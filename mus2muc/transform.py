import argparse
import os
from mus2muc.ltlf_parser import parse_formula_as_object
from mus2muc.ltlf_parser.syntax import Conjunction
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("root_folder", type=str)
    p.add_argument("target_folder", type=str)

    args = p.parse_args()
    return args.root_folder, args.target_folder


def recurse_on_formula(formula):
    stack = [formula]
    conjuncts = []

    while len(stack) > 0:
        top = stack.pop()
        if isinstance(top, Conjunction):
            stack.extend(top.children())
        else:
            conjuncts.append(top)

    return conjuncts


def check_if_conjunctive(formula_path):
    try:
        formula_object = parse_formula_as_object(Path(formula_path).open().read())
        if not isinstance(formula_object, Conjunction):
            print(formula_path, "is not a conjunction, would have a single MUS...")
            return []

        return recurse_on_formula(formula_object)

    except:
        print(formula_path, "does not have a compatible grammar.")
        return []


def main():
    root_folder, target_folder = parse_args()

    for subfolder, dirs, files in os.walk(root_folder):
        if len(dirs) != 0:
            continue

        for f in files:
            formula_path = os.path.sep.join([subfolder, f])
            children = check_if_conjunctive(formula_path)
            if len(children) > 0:
                subfolder_structure = formula_path.split(os.path.sep)[1:-1]
                name = Path(formula_path).name
                output_folder = Path(target_folder, *subfolder_structure)

                os.makedirs(output_folder, exist_ok=True)

                output_file = output_folder / name
                with output_file.open("w") as f:
                    # print("Writing", formula_path, "to", output_file)
                    for conjid, conjunct in enumerate(children):
                        f.write(f"P{conjid} := {conjunct};")
                        f.write("\n")
                        f.flush()
