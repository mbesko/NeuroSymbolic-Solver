from dataclasses import dataclass, field
from typing import List, Optional

VARIABLE_NAMES = {'x', 'y', 'z', 'u', 'v', 'w'}


@dataclass(frozen=True)
class Term:
    name: str
    args: List['Term'] = field(default_factory=list)

    def __repr__(self):
        if not self.args:
            return self.name
        return f"{self.name}({', '.join(map(str, self.args))})"

    def is_variable(self):
        if self.args:
            return False

        first_char = self.name[0].lower()

        return first_char in VARIABLE_NAMES


@dataclass(frozen=True)
class Literal:
    name: str
    args: List[Term]
    negated: bool = False

    def __repr__(self):
        prefix = "¬" if self.negated else ""
        return f"{prefix}{self.name}({', '.join(map(str, self.args))})"


@dataclass
class Clause:
    literals: List[Literal]
    origin: Optional[str] = None
    id: int = -1

    def __repr__(self):
        if not self.literals:
            return "□ (Пустая клауза - Противоречие)"
        return " ∨ ".join(map(str, self.literals))

    def __hash__(self):
        return hash(frozenset(map(str, self.literals)))

    def __eq__(self, other):
        if not isinstance(other, Clause): return False
        return set(map(str, self.literals)) == set(map(str, other.literals))

    def __len__(self):
        return len(self.literals)
