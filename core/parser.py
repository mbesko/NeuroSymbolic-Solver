import re
import json
from .types import Clause, Literal, Term


def parse_term(text: str) -> Term:
    text = text.strip()
    if '(' not in text: return Term(text)
    name = text.split('(')[0].strip()
    args_str = text[len(name) + 1: -1]
    args = []
    depth = 0
    buffer = []
    for char in args_str:
        if char == ',' and depth == 0:
            args.append(parse_term("".join(buffer)))
            buffer = []
        else:
            if char == '(': depth += 1
            if char == ')': depth -= 1
            buffer.append(char)
    if buffer: args.append(parse_term("".join(buffer)))
    return Term(name, args)


def parse_literal(text: str) -> Literal:
    text = text.strip()
    negated = False
    if text.startswith(('¬', '~', '!')):
        negated = True
        text = text[1:].strip()
    elif text.lower().startswith('not '):
        negated = True
        text = text[4:].strip()

    term = parse_term(text)
    return Literal(term.name, term.args, negated)


def parse_clauses_from_llm(text: str) -> list[Clause]:
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            raw_list = json.loads(match.group(0))
        else:
            raw_list = [line for line in text.split('\n') if '(' in line]
    except:
        raw_list = text.split('\n')

    clauses = []
    for raw_line in raw_list:
        if not isinstance(raw_line, str): continue
        clean_line = raw_line.strip().strip(',').strip('"').strip("'")
        if not clean_line: continue

        parts = re.split(r'\s*∨\s*|\s*v\s*|\s*\|\|\s*', clean_line)
        lits = [parse_literal(p) for p in parts if p.strip()]
        if lits:
            clauses.append(Clause(lits))
    return clauses