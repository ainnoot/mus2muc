from collections import defaultdict
from typing import Set, Dict, Sequence

import clingo  # type: ignore
from mus2muc.ltlf_parser.parser_constants import Constants as ParserConstants
from mus2muc.ltlf_parser.reify_interface import Reify


def clingo_symbol(name: str, args: Sequence[int]) -> clingo.Symbol:
    return clingo.Function(name, [clingo.Number(x) for x in args])


def add_in_backend(b: clingo.Backend, symbol: clingo.Symbol) -> None:
    lit = b.add_atom(symbol)
    b.add_rule([lit], [])


class IDPool:
    def __init__(self, start_from: int) -> None:
        self.objects: Dict[object, int] = defaultdict(lambda: self._next_id())
        self.i_: int = start_from

    def _next_id(self) -> int:
        i = self.i_
        self.i_ += 1
        return i

    def id(self, obj: object) -> int:
        return self.objects[obj]


class ReifyFormulaAsFacts(Reify[int, Set[clingo.Symbol]]):
    def __init__(self, start_index) -> None:
        super().__init__()
        self.pool: IDPool = IDPool(start_index)
        self.facts: Set[clingo.Symbol] = set()

    def result(self) -> Set[clingo.Symbol]:
        return self.facts

    def constant(self, name: str) -> int:
        id = self.pool.id((name,))
        self.facts.add(clingo_symbol(name, [id]))
        return id

    def reify_unary(self, f: int, name: str) -> int:
        id = self.pool.id((name, f))
        self.facts.add(clingo_symbol(name, [id, f]))
        return id

    def reify_binary(self, lhs: int, rhs: int, name: str) -> int:
        id = self.pool.id((name, lhs, rhs))
        self.facts.add(clingo_symbol(name, [id, lhs, rhs]))
        return id

    def reify_variadic(self, fs: Sequence[int], name: str) -> int:
        id = self.pool.id((name, *sorted(fs)))
        for f in fs:
            self.facts.add(clingo_symbol(name, [id, f]))
        return id

    def true(self) -> int:
        return self.constant(ParserConstants.TRUE)

    def false(self) -> int:
        return self.constant(ParserConstants.FALSE)

    def last(self) -> int:
        return self.constant(ParserConstants.LAST)

    def proposition(self, string: str) -> int:
        id = self.pool.id((ParserConstants.ATOMIC, string))
        self.facts.add(
            clingo.Function(
                ParserConstants.ATOMIC, [clingo.Number(id), clingo.String(string)]
            )
        )
        return id

    def next(self, f: int) -> int:
        return self.reify_unary(f, ParserConstants.NEXT)

    def weak_next(self, f: int) -> int:
        return self.reify_unary(f, ParserConstants.WEAK_NEXT)
        # return self.disjunction((self.last(), self.next(f)))

    def until(self, lhs: int, rhs: int) -> int:
        return self.reify_binary(lhs, rhs, ParserConstants.UNTIL)

    def release(self, lhs: int, rhs: int) -> int:
        return self.reify_binary(lhs, rhs, ParserConstants.RELEASE)

    def weak_until(self, lhs: int, rhs: int) -> int:
        # return self.reify_binary(lhs, rhs, ParserConstants.WEAK_UNTIL)
        return self.disjunction((self.until(lhs, rhs), self.always(lhs)))

    def strong_release(self, lhs: int, rhs: int) -> int:
        # return self.reify_binary(lhs, rhs, ParserConstants.STRONG_RELEASE)
        return self.conjunction((self.release(lhs, rhs), self.eventually(lhs)))

    def equivalence(self, lhs: int, rhs: int) -> int:
        # return self.reify_binary(lhs, rhs, ParserConstants.EQUALS)
        return self.conjunction((self.implies(lhs, rhs), self.implies(rhs, lhs)))

    def implies(self, lhs: int, rhs: int) -> int:
        # return self.reify_binary(lhs, rhs, ParserConstants.IMPLIES)
        return self.disjunction((self.negate(lhs), rhs))

    def eventually(self, f: int) -> int:
        # return self.reify_unary(f, ParserConstants.EVENTUALLY)
        return self.until(self.true(), f)

    def always(self, f: int) -> int:
        # return self.reify_unary(f, ParserConstants.ALWAYS)
        return self.release(self.false(), f)

    def negate(self, f: int) -> int:
        return self.reify_unary(f, ParserConstants.NEGATE)

    def conjunction(self, fs: Sequence[int]) -> int:
        return self.reify_variadic(fs, ParserConstants.CONJUNCTION)

    def disjunction(self, fs: Sequence[int]) -> int:
        return self.reify_variadic(fs, ParserConstants.DISJUNCTION)

    def mark_as_root(self, f: int) -> int:
        self.facts.add(clingo_symbol(ParserConstants.ROOT, [f]))
        return f
