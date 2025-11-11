from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Sequence, List

import clingo


def integer_sequence():
    x = 1
    while True:
        yield x
        x += 1


__formula_id_sequence__ = integer_sequence()
__formula_ids__ = dict()


@dataclass(frozen=True)
class Formula(ABC):
    @abstractmethod
    def __code__(self):
        pass

    def __post_init__(self):
        h = self.__code__()
        if h not in __formula_ids__:
            i = next(__formula_id_sequence__)
            __formula_ids__[h] = i

    @property
    def id(self):
        return clingo.Number(__formula_ids__[self.__code__()])

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def children(self) -> List:
        pass


@dataclass(frozen=True)
class Atomic(Formula, ABC):
    def __str__(self) -> str:
        return self.symbol()

    def children(self) -> List:
        return []


@dataclass(frozen=True)
class Truth(Atomic):
    def __code__(self):
        return ("true",)

    @property
    def id(self):
        return clingo.Function("true")

    def symbol(self) -> str:
        return "True"


@dataclass(frozen=True)
class Faux(Atomic):
    def __code__(self):
        return ("false",)

    @property
    def id(self):
        return clingo.Function("false")

    def symbol(self) -> str:
        return "False"


@dataclass(frozen=True)
class Proposition(Atomic):
    value: str

    def __code__(self):
        return ("proposition", self.value)

    def symbol(self) -> str:
        return self.value


@dataclass(frozen=True)
class Unary(Formula, ABC):
    f: Formula

    def dual(self):
        pass

    def __str__(self) -> str:
        return "({} {})".format(self.symbol(), self.f)

    def children(self) -> List:
        return [self.f]


@dataclass(frozen=True)
class Next(Unary):
    def __code__(self):
        return ("next", *self.f.__code__())

    def symbol(self) -> str:
        return "X"


@dataclass(frozen=True)
class Eventually(Unary):
    def __code__(self):
        return ("eventually", *self.f.__code__())

    def symbol(self) -> str:
        return "F"


@dataclass(frozen=True)
class Always(Unary):
    def __code__(self):
        return ("always", *self.f.__code__())

    def symbol(self) -> str:
        return "G"


@dataclass(frozen=True)
class WeakNext(Unary):
    def __code__(self):
        return ("weak-next", *self.f.__code__())

    def symbol(self) -> str:
        return "wX"


@dataclass(frozen=True)
class Negate(Unary):
    def __code__(self):
        return ("negate", *self.f.__code__())

    def symbol(self) -> str:
        return "~"


@dataclass(frozen=True)
class Binary(Formula, ABC):
    lhs: Formula
    rhs: Formula

    def __str__(self) -> str:
        return "({} {} {})".format(self.lhs, self.symbol(), self.rhs)

    def children(self) -> List:
        return [self.lhs, self.rhs]


@dataclass(frozen=True)
class Release(Binary):
    def __code__(self):
        return ("release", (self.lhs.__code__(), self.rhs.__code__()))

    def symbol(self) -> str:
        return "R"


@dataclass(frozen=True)
class StrongRelease(Binary):
    def __code__(self):
        return ("strong_release", (self.lhs.__code__(), self.rhs.__code__()))

    def symbol(self) -> str:
        return "M"


@dataclass(frozen=True)
class Until(Binary):
    def __code__(self):
        return ("until", (self.lhs.__code__(), self.rhs.__code__()))

    def symbol(self) -> str:
        return "U"


@dataclass(frozen=True)
class StrongRelease(Binary):
    def __code__(self):
        return ("weak_until", (self.lhs.__code__(), self.rhs.__code__()))

    def symbol(self) -> str:
        return "W"


@dataclass(frozen=True)
class Implies(Binary):
    def __code__(self):
        return ("implies", (self.lhs.__code__(), self.rhs.__code__()))

    def symbol(self) -> str:
        return "->"


@dataclass(frozen=True)
class Equals(Binary):
    def __code__(self):
        return ("equals", (self.lhs.__code__(), self.rhs.__code__()))

    def symbol(self) -> str:
        return "<->"


@dataclass(frozen=True)
class Variadic(Formula, ABC):
    fs: Sequence[Formula]

    def __str__(self) -> str:
        return "({})".format((" " + self.symbol() + " ").join(str(x) for x in self.fs))

    def children(self) -> List:
        return list(self.fs)


@dataclass(frozen=True)
class Conjunction(Variadic):
    def __code__(self):
        return ("conjunction", *[f.__code__() for f in self.fs])

    def symbol(self) -> str:
        return "&"


@dataclass(frozen=True)
class Disjunction(Variadic):
    def __code__(self):
        return ("disjunction", *[f.__code__() for f in self.fs])

    def symbol(self) -> str:
        return "|"


class FormulaBuilder:
    @staticmethod
    def proposition(value: str):
        return Proposition(value)

    @staticmethod
    def last():
        return WeakNext(Faux())

    @staticmethod
    def true():
        return Truth()

    @staticmethod
    def false():
        return Faux()

    @staticmethod
    def next(f: Formula):
        return Next(f)

    @staticmethod
    def always(f: Formula):
        return Always(f)

    @staticmethod
    def eventually(f: Formula):
        return Eventually(f)

    @staticmethod
    def weak_next(f: Formula):
        return WeakNext(f)

    @staticmethod
    def negate(f: Formula):
        return Negate(f)

    @staticmethod
    def until(f: Formula, g: Formula):
        return Until(f, g)

    @staticmethod
    def release(f: Formula, g: Formula):
        return Release(f, g)

    @staticmethod
    def weak_until(f: Formula, g: Formula):
        # a W b
        # G(a) | (a U b)
        return Disjunction([FormulaBuilder.always(f), FormulaBuilder.until(f, g)])

    @staticmethod
    def strong_release(f: Formula, g: Formula):
        # ~(~a W ~b)
        # ~(G(~a) | (~a U ~b))
        # ~((false R ~a) | (~a U ~b))
        # true U a & (a R b))
        return Conjunction(
            [FormulaBuilder.until(Truth(), f), FormulaBuilder.release(f, g)]
        )

    @staticmethod
    def implication(f: Formula, g: Formula):
        # a -> b
        # ~a | b
        return Implies(f, g)

    @staticmethod
    def equivalence(f: Formula, g: Formula):
        return Equals(f, g)

    @staticmethod
    def conjunction(fs: List[Formula]):
        return Conjunction(fs)

    @staticmethod
    def disjunction(fs: List[Formula]):
        return Disjunction(fs)
