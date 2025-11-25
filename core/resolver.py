from typing import List, Tuple, Generator, Set
from .types import Clause, Literal, Term
from .unification import unify, apply_subst_term


def instantiate_literal(target: Literal, substitution: dict) -> Literal:
    updated_args = [apply_subst_term(arg, substitution) for arg in target.args]
    return Literal(target.name, updated_args, target.negated)


def refresh_var_names(clause: Clause, uid: int) -> Clause:
    var_map = {}

    def _transform_term(t: Term) -> Term:
        if t.is_variable():
            new_name = f"{t.name}_{uid}"
            var_map[t.name] = new_name
            return Term(new_name)
        new_sub_args = [_transform_term(sub) for sub in t.args]
        return Term(t.name, new_sub_args)

    new_literals = []
    for lit in clause.literals:
        refreshed_args = [_transform_term(arg) for arg in lit.args]
        new_literals.append(Literal(lit.name, refreshed_args, lit.negated))

    return Clause(new_literals, clause.origin, clause.id)


def is_trivial_tautology(clause: Clause) -> bool:

    lits = clause.literals
    count = len(lits)
    for i in range(count):
        for j in range(i + 1, count):
            l1, l2 = lits[i], lits[j]
            if l1.name == l2.name and l1.args == l2.args and l1.negated != l2.negated:
                return True
    return False


def generate_resolvents(parent_a: Clause, parent_b: Clause) -> Generator[Tuple[Clause, str], None, None]:

    for idx_a, lit_a in enumerate(parent_a.literals):
        for idx_b, lit_b in enumerate(parent_b.literals):

            if lit_a.name == lit_b.name and lit_a.negated != lit_b.negated:

                subst = unify(lit_a.args, lit_b.args, {})

                if subst is not None:
                    remainder_a = [
                        instantiate_literal(l, subst)
                        for k, l in enumerate(parent_a.literals) if k != idx_a
                    ]
                    remainder_b = [
                        instantiate_literal(l, subst)
                        for k, l in enumerate(parent_b.literals) if k != idx_b
                    ]

                    unique_pool = {}
                    for lit in remainder_a + remainder_b:
                        unique_pool[str(lit)] = lit

                    child_literals = list(unique_pool.values())
                    child_clause = Clause(child_literals)

                    if not is_trivial_tautology(child_clause):
                        desc = f"Резолюция ({parent_a.id}, {parent_b.id}) по {lit_a}/{lit_b}"
                        yield child_clause, desc


def prove_statement(initial_clauses: List[Clause]) -> Tuple[bool, List[str]]:

    axiom_pool = initial_clauses[:]
    for idx, c in enumerate(axiom_pool):
        c.id = idx + 1
        c.origin = "Аксиома"

    trace = [f"[{c.id}] {c}" for c in axiom_pool]

    existing_hashes = {hash(c) for c in axiom_pool}

    HARD_LIMIT_STEPS = 600
    current_step = 0
    unique_counter = 0

    while current_step < HARD_LIMIT_STEPS:
        found_new_info = False

        axiom_pool.sort(key=lambda x: len(x))

        pool_size = len(axiom_pool)


        lookback_window = 0 if current_step == 0 else max(0, pool_size - 15)

        for i in range(pool_size):
            for j in range(i + 1, pool_size):

                if i < lookback_window and j < lookback_window:
                    continue

                clause_1 = axiom_pool[i]
                clause_2 = axiom_pool[j]

                unique_counter += 1
                c1_ready = refresh_var_names(clause_1, unique_counter)
                c2_ready = refresh_var_names(clause_2, unique_counter + 1)
                unique_counter += 1

                for offspring, method_desc in generate_resolvents(c1_ready, c2_ready):

                    if not offspring.literals:
                        trace.append(f"ШАГ {current_step + 1}: {method_desc} => 🟥 ПУСТАЯ КЛАУЗА (ПРОТИВОРЕЧИЕ)")
                        return True, trace

                    h_val = hash(offspring)
                    if h_val not in existing_hashes:
                        existing_hashes.add(h_val)

                        offspring.id = len(axiom_pool) + 1
                        offspring.origin = method_desc
                        axiom_pool.append(offspring)

                        trace.append(f"ШАГ {current_step + 1}: {method_desc} => [{offspring.id}] {offspring}")

                        found_new_info = True
                        current_step += 1

                        if current_step >= HARD_LIMIT_STEPS:
                            break

                if current_step >= HARD_LIMIT_STEPS:
                    break
            if current_step >= HARD_LIMIT_STEPS:
                break

        if not found_new_info:
            break

    trace.append("Поиск остановлен: противоречие не найдено (или превышен лимит шагов).")
    return False, trace
