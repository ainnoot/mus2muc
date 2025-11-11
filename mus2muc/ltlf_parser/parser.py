from typing import TypeVar, Set, Type, Sequence

import clingo  # type: ignore
import lark  # type: ignore
from lark import Lark, Transformer
from pathlib import Path
from mus2muc.ltlf_parser.parser_constants import Constants as ParserConstants
from mus2muc.ltlf_parser.reify_as_atoms import ReifyFormulaAsFacts
from mus2muc.ltlf_parser.reify_as_object import ReifyFormulaAsObject
from mus2muc.exceptions import ParsingError, UnsupportedOperator
from mus2muc.ltlf_parser.reify_interface import Reify
from mus2muc.constants import Constants

T = TypeVar("T")
G = TypeVar("G")


class LTLfFlatTransformer(Transformer[T]):
    def __init__(self, start_from: int) -> None:
        """Initiaflize."""
        super().__init__()
        self.reify: Reify[T, G] = ReifyFormulaAsFacts(start_from)
        assert start_from > 0
        self.annotation_rules = []

    def start(self, args: Sequence[T]) -> G:  # type: ignore
        assert all([token.value == "\n" for token in args])
        self.reify.mark_as_root(0)
        true_id = self.reify.true()
        self.annotation_rules.append(f"conjunction(0, {true_id}).")
        return self.reify.result()

    def get_program(self):
        from itertools import chain

        return "\n".join(
            chain(
                [str(fact) + "." for fact in self.reify.result()], self.annotation_rules
            )
        )

    def formula_id(self, args):
        return args[0].value

    def formula_line(self, args):
        conjunct_identifier, conjunct_root = args
        mus_atom = f'__mus__("{conjunct_identifier}")'
        rule = f"conjunction(0, {conjunct_root}) :- {mus_atom}."
        self.annotation_rules.append(f"{{ {mus_atom} }}.")
        self.annotation_rules.append(rule)
        return lark.Discard

    def ltlf_formula(self, args: Sequence[T]) -> T:
        return args[0]

    def ltlf_unaryop(self, args: Sequence[T]) -> T:
        return args[0]

    def ltlf_equivalence(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Release is not supported!")

            lhs, rhs = subformulas
            return self.reify.equivalence(lhs, rhs)

        raise ParsingError

    def ltlf_implication(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Implication is not supported!")
            lhs, rhs = subformulas
            return self.reify.implies(lhs, rhs)

        raise ParsingError

    def ltlf_or(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            return self.reify.disjunction(subformulas)

        raise ParsingError

    def ltlf_and(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            return self.reify.conjunction(subformulas)

        raise ParsingError

    def ltlf_until(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Until is not supported!")
            lhs, rhs = subformulas
            return self.reify.until(lhs, rhs)

        raise ParsingError

    def ltlf_weak_until(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic WeakUntil is not supported!")
            lhs, rhs = subformulas
            return self.reify.weak_until(lhs, rhs)

        raise ParsingError

    def ltlf_release(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Release is not supported!")
            lhs, rhs = subformulas
            return self.reify.release(lhs, rhs)

        raise ParsingError

    def ltlf_strong_release(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic StrongRelease is not supported!")
            lhs, rhs = subformulas
            return self.reify.strong_release(lhs, rhs)

        raise ParsingError

    def ltlf_always(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.always(args[1])

    def ltlf_eventually(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.eventually(args[1])

    def ltlf_next(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.next(args[1])

    def ltlf_weak_next(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.weak_next(args[1])

    def ltlf_not(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.negate(args[1])

    def ltlf_wrapped(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]
        return args[1]

    def symbol(self, args: Sequence[lark.Token]) -> str:
        string = "".join(x.value for x in args)
        return string.replace("'", '"')

    def ltlf_atom(self, args: Sequence[str]) -> T:
        if args[0].lower() == ParserConstants.TRUE:
            return self.ltlf_true(args)

        elif args[0].lower() == ParserConstants.FALSE:
            return self.ltlf_false(args)

        elif args[0].lower() in (ParserConstants.LAST, ParserConstants.END):
            return self.ltlf_last(args)

        else:
            return self.reify.proposition(args[0])

    def ltlf_true(self, _args: Sequence[str]) -> T:
        return self.reify.true()

    def ltlf_false(self, _args: Sequence[str]) -> T:
        return self.reify.false()

    def ltlf_last(self, _args: Sequence[str]) -> T:
        return self.reify.last()


def make_choice(atom_strings: Sequence[str]):
    return "{" + ";".join(a for a in atom_strings) + "}."


class LTLfObjectTransformer(Transformer[T]):
    def __init__(self) -> None:
        """Initiaflize."""
        super().__init__()
        self.reify: Reify[T, G] = ReifyFormulaAsObject()

    def start(self, args: Sequence[T]) -> G:  # type: ignore
        self.reify.mark_as_root(args[0])
        return_value = self.reify.result()
        return return_value

    def ltlf_formula(self, args: Sequence[T]) -> T:
        return args[0]

    def ltlf_unaryop(self, args: Sequence[T]) -> T:
        return args[0]

    def ltlf_equivalence(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Release is not supported!")

            lhs, rhs = subformulas
            return self.reify.equivalence(lhs, rhs)

        raise ParsingError

    def ltlf_implication(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Implication is not supported!")
            lhs, rhs = subformulas
            return self.reify.implies(lhs, rhs)

        raise ParsingError

    def ltlf_or(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            return self.reify.disjunction(subformulas)

        raise ParsingError

    def ltlf_and(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            return self.reify.conjunction(subformulas)

        raise ParsingError

    def ltlf_until(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Until is not supported!")
            lhs, rhs = subformulas
            return self.reify.until(lhs, rhs)

        raise ParsingError

    def ltlf_weak_until(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic WeakUntil is not supported!")
            lhs, rhs = subformulas
            return self.reify.weak_until(lhs, rhs)

        raise ParsingError

    def ltlf_release(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic Release is not supported!")
            lhs, rhs = subformulas
            return self.reify.release(lhs, rhs)

        raise ParsingError

    def ltlf_strong_release(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        if (len(args) - 1) % 2 == 0:
            subformulas = args[::2]
            if len(subformulas) != 2:
                raise UnsupportedOperator("Variadic StrongRelease is not supported!")
            lhs, rhs = subformulas
            return self.reify.strong_release(lhs, rhs)

        raise ParsingError

    def ltlf_always(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.always(args[1])

    def ltlf_eventually(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.eventually(args[1])

    def ltlf_next(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.next(args[1])

    def ltlf_weak_next(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.weak_next(args[1])

    def ltlf_not(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]

        return self.reify.negate(args[1])

    def ltlf_wrapped(self, args: Sequence[T]) -> T:
        if len(args) == 1:
            return args[0]
        return args[1]

    def symbol(self, args: Sequence[lark.Token]) -> str:
        string = "".join(x.value for x in args)
        return string.replace("'", '"')

    def ltlf_atom(self, args: Sequence[str]) -> T:
        if args[0].lower() == ParserConstants.TRUE:
            return self.ltlf_true(args)

        elif args[0].lower() == ParserConstants.FALSE:
            return self.ltlf_false(args)

        elif args[0].lower() in (ParserConstants.LAST, ParserConstants.END):
            return self.ltlf_last(args)

        else:
            return self.reify.proposition(args[0])

    def ltlf_true(self, _args: Sequence[str]) -> T:
        return self.reify.true()

    def ltlf_false(self, _args: Sequence[str]) -> T:
        return self.reify.false()

    def ltlf_last(self, _args: Sequence[str]) -> T:
        return self.reify.last()


def parse_formula_as_object(formula_string: str):
    GRAMMAR = Path(__file__).parent / "object_grammar.lark"
    parser = Lark(GRAMMAR.read_text(), parser="lalr", start="start")
    transformer = LTLfObjectTransformer()
    tree = parser.parse(formula_string)
    return transformer.transform(tree)  # type: ignore


def parse_formula_as_facts(formula_string: str, start_from: int) -> G:
    GRAMMAR = Path(__file__).parent / "grammar.lark"
    parser = Lark(GRAMMAR.read_text(), parser="lalr", start="start")
    transformer = LTLfFlatTransformer(start_from)
    tree = parser.parse(formula_string)
    return transformer.transform(tree)  # type: ignore


def parse_formulae_and_annotate(formula_string: str, target_path: Path, mode: str):
    GRAMMAR = Path(__file__).parent / "grammar.lark"
    parser = Lark(GRAMMAR.read_text(), parser="lalr", start="start")
    transformer = LTLfFlatTransformer(1)
    tree = parser.parse(formula_string)
    transformer.transform(tree)

    with target_path.open(mode) as f:
        f.write(transformer.get_program())
        f.flush()