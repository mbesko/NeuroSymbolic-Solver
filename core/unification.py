from typing import Dict, Optional
from .types import Term

Substitution = Dict[str, Term]


def apply_subst_term(term: Term, subst: Substitution) -> Term:
    if term.name in subst and not term.args:
        return subst[term.name]
    new_args = [apply_subst_term(arg, subst) for arg in term.args]
    return Term(term.name, new_args)


def occur_check(var: Term, x: Term, subst: Substitution) -> bool:
    if var == x: return True
    if isinstance(x, Term) and x.name in subst:
        return occur_check(var, subst[x.name], subst)
    elif isinstance(x, Term):
        return any(occur_check(var, arg, subst) for arg in x.args)
    return False


def unify(x: Term | list, y: Term | list, subst: Substitution) -> Optional[Substitution]:
    if subst is None: return None
    if x == y: return subst

    if isinstance(x, Term) and x.is_variable():
        return unify_var(x, y, subst)
    if isinstance(y, Term) and y.is_variable():
        return unify_var(y, x, subst)

    if isinstance(x, Term) and isinstance(y, Term):
        if x.name != y.name or len(x.args) != len(y.args): return None
        return unify(x.args, y.args, subst)

    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): return None
        if not x: return subst
        return unify(x[1:], y[1:], unify(x[0], y[0], subst))
    return None


def unify_var(var: Term, x: Term, subst: Substitution) -> Optional[Substitution]:
    if var.name in subst:
        return unify(subst[var.name], x, subst)
    if isinstance(x, Term) and x.name in subst:
        return unify(var, subst[x.name], subst)
    if occur_check(var, x, subst):
        return None

    new_subst = subst.copy()
    new_subst[var.name] = x
    for k, v in new_subst.items():
        if k != var.name:
            new_subst[k] = apply_subst_term(v, {var.name: x})
    return new_subst