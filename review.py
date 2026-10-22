"""Restricted controlled-English compiler and auditable Euler reviews."""
import copy
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path
from falsifylab import ENGINE_SHA256, ValidationError, rational, Expression

REVIEW_VERSION = '0.2.0'
SOURCE = {'review': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'engine': ENGINE_SHA256}
GRAMMAR = "Explicit Euler for y' = -rate*y with rate = 1 keeps squared amplitude at or below its initial value for every real initial y and every h in [0, 3]."
NUM = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:/\d+)?'
PATTERN = re.compile(r"Explicit Euler for y'\s*=\s*-rate\s*\*\s*y with rate\s*=\s*("+NUM+r") (?:does not increase squared amplitude|keeps squared amplitude at or below its initial value) for every real initial y and every h in \[\s*("+NUM+r")\s*,\s*("+NUM+r")\s*\]\.?")

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def propose(raw_text, search_min='0', search_max='3', step='1/4'):
    if not isinstance(raw_text, str) or not 1 <= len(raw_text) <= 3000:
        raise ValidationError('Enter a claim using the example sentence, up to 3,000 characters.')
    match = PATTERN.fullmatch(' '.join(raw_text.split()))
    if not match:
        raise ValidationError('Use the displayed example sentence and set its rate and interval, then compile again.')
    rate, lo, hi = [rational(x) for x in match.groups()]
    smin, smax, stride = [rational(x) for x in (search_min, search_max, step)]
    if rate <= 0 or lo < 0 or hi < lo:
        raise ValidationError('This model requires a positive constant rate and a closed non-negative h interval.')
    if smin < 0 or smax < smin or stride <= 0:
        raise ValidationError('Search bounds must be non-negative and ordered; step must be positive.')
    count = int((smax-smin)//stride)+1
    if count > 9990:
        raise ValidationError('At most 9,990 grid points plus boundary probes; increase the step.')
    boundary = Fraction(2)/rate
    candidates = sorted({smin,smax,Fraction(0),1/rate,boundary,boundary-stride,boundary+stride})
    probes = [str(x) for x in candidates if smin <= x <= smax]
    p = {'schema_version':2, 'compiler_version':REVIEW_VERSION, 'source':dict(SOURCE),
         'raw_claim':raw_text, 'interpretation':{
             'model':"y' = -rate*y", 'method':'explicit Euler', 'rate':str(rate),
             'property':'squared amplitude bounded by its initial value after one step', 'quantifier':'for every real initial y and every h in the claim interval',
             'claim_domain':{'h_min':str(lo),'h_max':str(hi)},
             'units':'Dimensionless normalized model.',
             'assertion':f'(1-({rate})*h)**2 <= 1',
             'reduction':'For y ≠ 0, divide by y²; for y = 0 the update remains zero.',
             'provenance':'Rate and interval are extracted directly from the claim.'},
         'plan':{'search_min':str(smin),'search_max':str(smax),'step':str(stride),
             'grid_points':count,'boundary_probes':probes,'budget':10000,
             'method':'Exact rational grid plus theory-guided boundary probes within the search interval.',
             'rationale':'Probe zero, zero amplification, the amplitude-preserving threshold 2/rate and its two sides.',
             'outside_claim_policy':'Record points beyond the claim interval as exploration.'}}
    return {**p,'digest':digest(p)}

def canonical_proposal(p):
    if not isinstance(p,dict):
        raise ValidationError('Proposal must be an object.')
    try:
        plan=p['plan']
        expected=propose(p['raw_claim'],plan['search_min'],plan['search_max'],plan['step'])
    except (KeyError,TypeError):
        raise ValidationError('Incomplete proposal.') from None
    if p != expected:
        raise ValidationError('Proposal changed or source version differs. Compile and confirm again.')
    return expected

def _analysis(rate,lo,hi):
    # Independent integer cross-multiplication, not the expression evaluator.
    # For positive rate and h>=0, non-expansion iff rate*h <= 2.
    a,b=rate.numerator,rate.denominator
    c,d=hi.numerator,hi.denominator
    holds=a*c <= 2*b*d
    return {'status':'condition_verified' if holds else 'exact_counterexample_identified',
            'coverage':'entire confirmed closed claim interval',
            'domain':{'h_min':str(lo),'h_max':str(hi)},
            'condition':'0 <= rate*h <= 2',
            'derivation':"y_next=(1-rate*h)y; y_next²-y²=rate*h*(rate*h-2)*y². For rate>0 and h>=0, y_next²<=y² for all real y exactly when rate*h<=2.",
            'verification':'Independent integer comparison of a*c and 2*b*d for rate=a/b and upper h=c/d.',
            'threshold':str(2/rate),
            'witness':None if holds else witness(rate,hi),
            'boundary_behavior':'At rate*h=2, amplitude is preserved while the sign alternates.'}

def witness(rate,h):
    nxt=1-rate*h
    return {'rate':str(rate),'h':str(h),'initial_y':'1','next_y':str(nxt),
            'squared_before':'1','squared_after':str(nxt*nxt),'squared_difference':str(nxt*nxt-1)}

def review(proposal,confirmed_digest,parent=None,_depth=0):
    if _depth > 7:
        raise ValidationError('Revision chain limited to eight reviews. Export before starting a new investigation.')
    p=canonical_proposal(proposal)
    if not isinstance(confirmed_digest,str) or confirmed_digest != p['digest']:
        raise ValidationError('Confirm the current proposal and search plan before review.')
    if parent is not None:
        if not isinstance(parent,dict):
            raise ValidationError('Invalid parent review.')
        try:
            checked=review(parent['proposal'],parent['proposal']['digest'],parent.get('parent'),_depth+1)
        except (KeyError,TypeError):
            raise ValidationError('Invalid parent review.') from None
        if checked != parent:
            raise ValidationError('Parent review was altered or cannot be reproduced.')
    i=p['interpretation'];plan=p['plan']
    rate=Fraction(i['rate']);lo=Fraction(i['claim_domain']['h_min']);hi=Fraction(i['claim_domain']['h_max'])
    smin=Fraction(plan['search_min']);stride=Fraction(plan['step'])
    points=sorted({smin+k*stride for k in range(plan['grid_points'])} | {Fraction(x) for x in plan['boundary_probes']})
    expr=Expression(i['assertion'],['h'],True)
    counts={'evaluated':0,'in_claim':0,'violations':0,'outside_claim':0,'outside_violations':0}
    samples=[];witnesses=[];explorations=[]
    for h in points:
        holds=expr.evaluate({'h':h});inside=lo<=h<=hi
        independently_holds = rate.numerator*h.numerator <= 2*rate.denominator*h.denominator
        if holds is not independently_holds:
            raise ValidationError('Internal inconsistency: evaluator and independent arithmetic disagree. No review issued.')
        counts['evaluated']+=1
        counts['in_claim' if inside else 'outside_claim']+=1
        if not holds:
            counts['violations' if inside else 'outside_violations']+=1
            target=witnesses if inside else explorations
            if len(target)<5:target.append(witness(rate,h))
        if len(samples)<120:samples.append({'h':str(h),'in_claim':inside,'holds':holds})
    grid_status='exact_counterexample_identified' if witnesses else ('exploration_recorded' if not counts['in_claim'] else 'exact_evaluations_recorded')
    data={'schema_version':2,'proposal':copy.deepcopy(p),'confirmed_digest':confirmed_digest,
          'parent':copy.deepcopy(parent),'parent_id':parent['review_id'] if parent else None,
          'grid':{'status':grid_status,'counts':counts,'witnesses':witnesses,'outside_exploration':explorations,'samples':samples,
                  "coverage":f"Search h ∈ [{plan['search_min']}, {plan['search_max']}], step {plan['step']}; claim h ∈ [{i['claim_domain']['h_min']}, {i['claim_domain']['h_max']}]."},
          'analysis':_analysis(rate,lo,hi),
          'evidence_summary':['Exact rational witnesses connect each result to a concrete assignment.',
                    'Search coverage and mathematical analysis are recorded alongside the confirmed claim.',
                    'Revisions preserve the original review and its evidence.',
                    'Source fingerprints and saved plans support deterministic replay.']}
    return {**data,'review_id':digest(data)}

def replay_report(report):
    if not isinstance(report,dict):raise ValidationError('Invalid report.')
    try:r=review(report['proposal'],report['confirmed_digest'],report.get('parent'))
    except KeyError:raise ValidationError('Invalid report.') from None
    if r!=report:raise ValidationError('Report mismatch: content or source differs.')
    return r

def markdown(report):
    lines=['# FalsifyLab — auditable Euler review','',f"Review ID: {report['review_id']}"]
    history=[];cur=report
    while cur:
        history.append(cur);cur=cur['parent']
    for r in reversed(history):
        p=r['proposal'];lines+=['','## '+('Current review' if r is report else 'Previous review (preserved)'),p['raw_claim'],
            'Review ID: '+r['review_id'],'Confirmed proposal: '+r['confirmed_digest'],
            'Claim domain: '+json.dumps(p['interpretation']['claim_domain']),
            'Search plan: '+json.dumps(p['plan']), 'Search outcome: '+r['grid']['status'].replace('_',' '),
            'Counts: '+json.dumps(r['grid']['counts']), 'Grid witnesses: '+json.dumps(r['grid']['witnesses']),
            'Outside-domain exploration: '+json.dumps(r['grid']['outside_exploration']),
            'Mathematical analysis: '+r['analysis']['status'].replace('_',' '), 'Analytical coverage: '+r['analysis']['coverage'],
            r['analysis']['derivation'], 'Analytical witness: '+json.dumps(r['analysis']['witness']),r['analysis']['boundary_behavior']]
    lines+=['','## Evidence record',*['- '+x for x in report['evidence_summary']],'','## Reproduce','python3 reproduce.py report.json',
            'Loaded source fingerprints: '+json.dumps(report['proposal']['source'])]
    return '\n'.join(lines)+'\n'
