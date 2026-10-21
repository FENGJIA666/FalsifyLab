"""Deterministic, exact-rational counterexample search. No eval or network calls."""
import ast
import hashlib
import itertools
import json
import operator
import re
from fractions import Fraction
from pathlib import Path

VERSION = '0.2.0'
ENGINE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
MAX_POINTS = 10000
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Mod: operator.mod}
CMP = {ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt,
       ast.GtE: operator.ge, ast.Eq: operator.eq, ast.NotEq: operator.ne}

class ValidationError(ValueError):
    pass

class EvaluationLimit(ValueError):
    pass

def rational(value):
    if not isinstance(value, (str, int)) or isinstance(value, bool) or len(str(value)) > 40:
        raise ValidationError('Use a short integer, decimal, or fraction.')
    token = str(value).strip()
    if not re.fullmatch(r'[+-]?(?:[0-9]+/[0-9]+|[0-9]+(?:\.[0-9]*)?|\.[0-9]+)', token):
        raise ValidationError('Use ordinary decimal numbers or integer fractions; scientific notation is not supported.')
    try:
        v = Fraction(token)
    except (ValueError, ZeroDivisionError):
        raise ValidationError('Invalid rational number.') from None
    if abs(v) > 1000000 or v.denominator > 1000000:
        raise ValidationError('Bounds must be within ±1,000,000; denominator <=1,000,000.')
    return v

class Expression:
    def __init__(self, source, names, predicate=False):
        if not isinstance(source, str) or not source.strip() or len(source) > 300:
            raise ValidationError('Expressions must contain 1–300 characters.')
        self.source = source
        try:
            self.root = ast.parse(source.strip(), mode='eval').body
        except (SyntaxError, RecursionError):
            raise ValidationError('Invalid expression syntax. Use ** for powers and == for equality.') from None
        if len(list(ast.walk(self.root))) > 100:
            raise ValidationError('Expression is too complex.')
        self.check(self.root, set(names), predicate)

    def check(self, n, names, predicate):
        if predicate:
            if isinstance(n, ast.Compare) and all(type(o) in CMP for o in n.ops):
                for v in [n.left, *n.comparators]:
                    self.check(v, names, False)
                return
            if isinstance(n, ast.BoolOp) and isinstance(n.op, (ast.And, ast.Or)):
                for v in n.values:
                    self.check(v, names, True)
                return
            raise ValidationError('Use comparisons joined by and/or for assumptions and assertions.')
        if isinstance(n, ast.Name) and n.id in names:
            return
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            rational(ast.get_source_segment(self.source.strip(), n))
            return
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            self.check(n.operand, names, False)
            return
        if isinstance(n, ast.BinOp) and type(n.op) in {*OPS, ast.Pow}:
            self.check(n.left, names, False)
            if isinstance(n.op, ast.Pow):
                if not isinstance(n.right, ast.Constant) or type(n.right.value) is not int or not 0 <= n.right.value <= 8:
                    raise ValidationError('Powers must be literal integers from 0 to 8.')
            else:
                self.check(n.right, names, False)
            return
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'abs' and len(n.args) == 1 and not n.keywords:
            self.check(n.args[0], names, False)
            return
        raise ValidationError('Supported: declared variables, rational constants, + - * / % **, abs(), comparisons, and/or.')

    def evaluate(self, env, node=None):
        n = self.root if node is None else node
        ev = lambda child: self.evaluate(env, child)
        if isinstance(n, ast.Constant):
            result = Fraction(ast.get_source_segment(self.source.strip(), n))
        elif isinstance(n, ast.Name):
            result = env[n.id]
        elif isinstance(n, ast.UnaryOp):
            result = -ev(n.operand) if isinstance(n.op, ast.USub) else ev(n.operand)
        elif isinstance(n, ast.BinOp):
            left, right = ev(n.left), ev(n.right)
            result = left ** int(right) if isinstance(n.op, ast.Pow) else OPS[type(n.op)](left, right)
        elif isinstance(n, ast.Call):
            result = abs(ev(n.args[0]))
        elif isinstance(n, ast.BoolOp):
            return all(ev(v) for v in n.values) if isinstance(n.op, ast.And) else any(ev(v) for v in n.values)
        elif isinstance(n, ast.Compare):
            left = ev(n.left)
            for op, child in zip(n.ops, n.comparators):
                right = ev(child)
                if not CMP[type(op)](left, right):
                    return False
                left = right
            return True
        else:
            raise ValidationError('Unsupported expression.')
        if result.numerator.bit_length() > 2048 or result.denominator.bit_length() > 2048:
            raise EvaluationLimit('Exact arithmetic size limit reached.')
        return result

    def trace(self, env):
        """Record only comparisons actually evaluated, including short-circuit skips."""
        rows = []
        source = self.source.strip()

        def skipped(node):
            if isinstance(node, ast.BoolOp):
                for child in node.values:
                    skipped(child)
            else:
                rows.append({'expression': ast.get_source_segment(source, node),
                             'values': [], 'holds': None, 'skipped': True,
                             'note': 'Not evaluated because an earlier Boolean operand determined the result.'})

        def visit(node):
            if isinstance(node, ast.BoolOp):
                is_and = isinstance(node.op, ast.And)
                for index, child in enumerate(node.values):
                    holds = visit(child)
                    if holds != is_and:
                        for remaining in node.values[index + 1:]:
                            skipped(remaining)
                        return holds
                return is_and
            nodes = [node.left, *node.comparators]
            left = self.evaluate(env, nodes[0])
            row = {'expression': ast.get_source_segment(source, node),
                   'values': [str(left)], 'holds': True, 'steps': []}
            rows.append(row)
            for index, (op, child) in enumerate(zip(node.ops, node.comparators)):
                right = self.evaluate(env, child)
                holds = CMP[type(op)](left, right)
                row['values'].append(str(right))
                row['steps'].append({'left': str(left), 'operator': type(op).__name__,
                                     'right': str(right), 'holds': holds})
                if not holds:
                    row['holds'] = False
                    row['skipped_operands'] = [ast.get_source_segment(source, rest)
                                               for rest in node.comparators[index + 1:]]
                    return False
                left = right
            return True

        visit(self.root)
        return rows

def validate(spec):
    if not isinstance(spec, dict):
        raise ValidationError('Specification must be a JSON object.')
    claim = spec.get('claim', '')
    if not isinstance(claim, str) or not 1 <= len(claim.strip()) <= 3000:
        raise ValidationError('Enter a claim (1–3000 characters).')
    if spec.get('confirmed') is not True:
        raise ValidationError('Confirm the mathematical interpretation before searching.')
    variables = spec.get('variables')
    if not isinstance(variables, list) or not 1 <= len(variables) <= 2:
        raise ValidationError('Define one or two variables.')
    names, grids, clean = [], [], []
    for v in variables:
        if not isinstance(v, dict):
            raise ValidationError('Each variable must be an object.')
        name = v.get('name', '')
        if not isinstance(name, str) or not re.fullmatch('[a-z][a-z0-9_]{0,11}', name) or name in names or name in {'abs', 'and', 'or'}:
            raise ValidationError('Use unique lowercase variable names (up to 12 characters).')
        lo, hi, step = (rational(v.get(k, '')) for k in ('min', 'max', 'step'))
        if step <= 0 or hi < lo:
            raise ValidationError('Step must be positive; maximum must be >= minimum.')
        count = int((hi-lo)//step) + 1
        if count > MAX_POINTS:
            raise ValidationError('Search is limited to 10,000 grid points.')
        names.append(name)
        grids.append([lo + i*step for i in range(count)])
        clean.append({'name': name, 'min': str(lo), 'max': str(hi), 'step': str(step)})
    if len(grids[0]) * (len(grids[1]) if len(grids) > 1 else 1) > MAX_POINTS:
        raise ValidationError('Cartesian grid exceeds 10,000 points; increase the step.')
    assumptions = spec.get('assumptions', '')
    if not isinstance(assumptions, str):
        raise ValidationError('Assumptions must be text.')
    pre = Expression(assumptions, names, True) if assumptions.strip() else None
    assertion = Expression(spec.get('assertion', ''), names, True)
    normalized = {'claim': claim.strip(), 'variables': clean, 'assumptions': assumptions.strip(),
                  'assertion': assertion.source.strip(), 'confirmed': True}
    return normalized, names, grids, pre, assertion

def search(spec):
    normalized, names, grids, pre, assertion = validate(spec)
    counts = {'grid_points': 0, 'excluded': 0, 'tested': 0, 'undefined': 0, 'violations': 0}
    witnesses, issues, samples = [], [], []
    for point in itertools.product(*grids):
        env = dict(zip(names, point))
        assignment = {k: str(v) for k, v in env.items()}
        counts['grid_points'] += 1
        try:
            if pre and not pre.evaluate(env):
                counts['excluded'] += 1
                continue
            holds = assertion.evaluate(env)
            counts['tested'] += 1
            if not holds:
                counts['violations'] += 1
                if len(witnesses) < 5:
                    witnesses.append({'assignment': assignment, 'comparisons': assertion.trace(env)})
            if len(samples) < 100:
                samples.append({'assignment': assignment, 'holds': holds})
        except (ZeroDivisionError, EvaluationLimit) as exc:
            counts['undefined'] += 1
            if len(issues) < 5:
                issues.append({'assignment': assignment, 'reason': 'Division by zero / undefined model' if isinstance(exc, ZeroDivisionError) else str(exc)})
    if witnesses:
        status = 'counterexample_found'
        conclusion = 'The confirmed universal assertion is false at an exact rational witness in this grid.'
    elif counts['undefined']:
        status = 'inconclusive'
        conclusion = 'No counterexample found, but some points could not be evaluated.'
    elif not counts['tested']:
        status = 'empty_domain'
        conclusion = 'No admissible points were tested. Check the assumptions and bounds.'
    else:
        status = 'no_counterexample_in_grid'
        conclusion = 'The assertion holds at all tested grid points. This is not a proof over a continuous or unbounded domain.'
    canonical = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    return {'schema_version': 1, 'engine_version': VERSION,
            'engine_sha256': ENGINE_SHA256,
            'spec_sha256': hashlib.sha256(canonical.encode()).hexdigest(),
            'spec': normalized, 'status': status, 'conclusion': conclusion, 'counts': counts,
            'witnesses': witnesses, 'issues': issues, 'samples': samples,
            'method': 'Exhaustive Cartesian rational grid; ascending variable order as supplied; all points visited; exact fractions; no random seed.',
            'limits': ['Only the human-confirmed mathematical statement is checked; natural-language equivalence is not verified.',
                       'Points between grid samples and outside the bounds are not tested.',
                       'A model counterexample is not experimental evidence against a physical law.',
                       'No literature retrieval or experimental measurements were performed.'],
            'next_steps': ['Inspect the witness and assumptions before revising the claim.' if witnesses else 'Refine the grid, widen bounds, or seek a symbolic proof.',
                           'For physical claims, validate units, model applicability, and experimental uncertainty separately.']}

def markdown(report):
    s, c = report['spec'], report['counts']
    lines = ['# FalsifyLab review', '', '## Claim', s['claim'], '', '## Result', report['status'], report['conclusion'],
             '', '## Human-confirmed formalization', f"For every sampled assignment: ({s['assumptions'] or 'no additional assumptions'}) implies ({s['assertion']}).",
             'Grid: ' + json.dumps(s['variables']), '', '## Evidence', json.dumps(c), report['method']]
    for w in report['witnesses']:
        lines += ['', 'Witness: ' + json.dumps(w['assignment']), json.dumps(w['comparisons'])]
    for issue in report['issues']:
        lines += ['', 'Unevaluated point: ' + json.dumps(issue)]
    lines += ['', '## Limits and uncertainty', *['- '+x for x in report['limits']], '', '## Next steps', *['- '+x for x in report['next_steps']],
              '', '## Reproduce', 'Save the JSON report as report.json and run: python3 reproduce.py report.json',
              'Engine: '+report['engine_version'], 'Engine SHA-256: '+report['engine_sha256'], 'Specification SHA-256: '+report['spec_sha256']]
    return '\n'.join(lines) + '\n'
