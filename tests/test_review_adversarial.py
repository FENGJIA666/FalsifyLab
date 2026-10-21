"""Independent adversarial contracts for the restricted review workflow."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

import review as subject
from falsifylab import ValidationError


def claim(rate='1', lo='0', hi='3'):
    return ("Explicit Euler for y' = -rate*y with rate = " + rate +
            " does not increase squared amplitude for every real initial y "
            "and every h in [" + lo + ", " + hi + "].")


def run(rate='1', lo='0', hi='3', search_min='0', search_max='3', step='1/4', parent=None):
    p = subject.propose(claim(rate, lo, hi), search_min, search_max, step)
    return subject.review(p, p['digest'], parent)


class AdversarialReviewTests(unittest.TestCase):
    def test_outside_counterexamples_do_not_refute_restricted_claim(self):
        r = run(hi='1')
        self.assertEqual(r['grid']['counts']['violations'], 0)
        self.assertGreater(r['grid']['counts']['outside_violations'], 0)
        self.assertEqual(r['grid']['witnesses'], [])
        self.assertEqual(r['analysis']['status'], 'supported_by_analytic_condition')
        for w in r['grid']['outside_exploration']:
            self.assertGreater(Fraction(w['h']), 1)

    def test_local_pass_does_not_overwrite_global_refutation(self):
        r = run(search_max='1')
        self.assertEqual(r['grid']['status'], 'no_counterexample_in_searched_points')
        self.assertEqual(r['analysis']['status'], 'refuted_by_analytic_witness')
        self.assertEqual(r['analysis']['witness']['h'], '3')
        self.assertEqual(r['analysis']['domain'], {'h_min': '0', 'h_max': '3'})

    def test_empty_intersection_is_not_a_grid_pass(self):
        r = run(hi='1', search_min='2', search_max='3')
        self.assertEqual(r['grid']['status'], 'no_admissible_points')
        self.assertEqual(r['grid']['counts']['in_claim'], 0)

    def test_nonexpansion_endpoint_is_not_strict_decay(self):
        r = run(lo='2', hi='2', search_min='2', search_max='2')
        self.assertEqual(r['grid']['counts']['violations'], 0)
        self.assertEqual(r['analysis']['status'], 'supported_by_analytic_condition')
        self.assertIn('not strict decay', r['analysis']['caveat'])

    def test_nonzero_witness_refutes_universal_initial_value(self):
        w = run(lo='3', hi='3')['analysis']['witness']
        self.assertNotEqual(Fraction(w['initial_y']), 0)
        self.assertGreater(Fraction(w['squared_after']), Fraction(w['squared_before']))

    def test_strict_grammar_rejects_semantic_additions(self):
        text = claim()
        bad = [text + ' It is also asymptotically stable.', 'Assume ' + text,
               text.replace('does not increase', 'strictly decreases'),
               text.replace('every real initial y', 'initial y = 0'),
               text.replace('-rate*y', '-rate*y*y'),
               text.replace('rate = 1', 'rate = 1 per second'),
               text.replace('rate = 1', 'rate = t'),
               text.replace('[0, 3]', '(0, 3)'),
               text.replace('squared amplitude', 'amplitude and preserves positivity')]
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                subject.propose(raw)

    def test_unsupported_physical_domains_rejected(self):
        for raw in [claim('0'), claim('-1'), claim(lo='-1'), claim(lo='3', hi='1')]:
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                subject.propose(raw)

    def test_invalid_search_plans_rejected(self):
        for a, b, step in [('-1', '3', '1'), ('3', '0', '1'), ('0', '3', '0'),
                           ('0', '3', '-1'), ('0', '3', '1/10000')]:
            with self.subTest(plan=(a, b, step)), self.assertRaises(ValidationError):
                subject.propose(claim(), a, b, step)

    def test_changed_text_requires_new_confirmation(self):
        old = subject.propose(claim())
        new = subject.propose(claim(hi='2'))
        with self.assertRaises(ValidationError):
            subject.review(new, old['digest'])

    def test_modified_executable_proposal_rejected_even_with_rehashed_digest(self):
        for field, value in [('assertion', 'h <= 100'), ('rate', '0'),
                             ('claim_domain', {'h_min': '0', 'h_max': '1'})]:
            p = subject.propose(claim())
            p['interpretation'][field] = value
            p['digest'] = subject.digest({k: v for k, v in p.items() if k != 'digest'})
            with self.subTest(field=field), self.assertRaises(ValidationError):
                subject.review(p, p['digest'])

    def test_changed_plan_and_source_rejected(self):
        for area, key, value in [('plan', 'boundary_probes', []),
                                 ('source', 'engine', 'old-engine'),
                                 ('plan', 'budget', 999999)]:
            p = copy.deepcopy(subject.propose(claim()))
            p[area][key] = value
            with self.subTest(key=key), self.assertRaises(ValidationError):
                subject.review(p, p['digest'])

    def test_proposal_source_is_not_mutable_global_alias(self):
        expected = copy.deepcopy(subject.SOURCE)
        try:
            p = subject.propose(claim())
            p['source']['engine'] = 'accidental-caller-mutation'
            fresh = subject.propose(claim())
            self.assertEqual(fresh['source'], expected)
        finally:
            subject.SOURCE.clear()
            subject.SOURCE.update(expected)

    def test_extra_trusted_looking_outcome_rejected(self):
        p = subject.propose(claim())
        p['analysis'] = {'status': 'supported_by_analytic_condition'}
        p['digest'] = subject.digest({k: v for k, v in p.items() if k != 'digest'})
        with self.assertRaises(ValidationError):
            subject.review(p, p['digest'])

    def test_revision_preserves_parent_and_links_hash(self):
        parent = run()
        before = copy.deepcopy(parent)
        revised = run(hi='2', parent=parent)
        self.assertEqual(parent, before)
        self.assertEqual(revised['parent'], before)
        self.assertEqual(revised['parent_id'], before['review_id'])
        self.assertEqual(parent['analysis']['status'], 'refuted_by_analytic_witness')
        self.assertEqual(revised['analysis']['status'], 'supported_by_analytic_condition')
        text = subject.markdown(revised)
        self.assertIn(claim(), text)
        self.assertIn(claim(hi='2'), text)

    def test_rehashed_forged_parent_rejected(self):
        parent = run()
        parent['analysis']['status'] = 'supported_by_analytic_condition'
        parent['analysis']['witness'] = None
        parent['review_id'] = subject.digest({k: v for k, v in parent.items() if k != 'review_id'})
        with self.assertRaises(ValidationError):
            run(hi='2', parent=parent)

    def test_tampered_report_cannot_replay(self):
        r = run()
        r['grid']['counts']['violations'] = 0
        with self.assertRaises(ValidationError):
            subject.replay_report(r)

    def test_report_deterministic_and_replayable(self):
        r = run()
        self.assertEqual(r, run())
        self.assertEqual(subject.replay_report(r), r)

    def test_independent_hand_computed_oracle_cases(self):
        # Expectations are fixed examples, not generated by the production threshold formula.
        cases = [('1/2', '4', True), ('1/2', '9/2', False),
                 ('1', '0', True), ('1', '2', True), ('1', '9/4', False),
                 ('3/2', '4/3', True), ('3/2', '3/2', False)]
        for rate, upper, expected in cases:
            with self.subTest(rate=rate, upper=upper):
                r = run(rate=rate, hi=upper)
                self.assertEqual(r['analysis']['status'] == 'supported_by_analytic_condition', expected)

    def test_analytic_oracle_does_not_reuse_expression_evaluator(self):
        # A locally passing grid must not be used to infer the global analytic result.
        with patch.object(subject.Expression, 'evaluate', return_value=True):
            r = run(search_max='1')
        self.assertEqual(r['grid']['counts']['violations'], 0)
        self.assertEqual(r['analysis']['status'], 'refuted_by_analytic_witness')

    def test_false_counterexample_from_broken_evaluator_is_blocked(self):
        with patch.object(subject.Expression, 'evaluate', return_value=False):
            with self.assertRaises(ValidationError):
                run(hi='1', search_max='1')

    def test_false_pass_from_broken_evaluator_is_blocked(self):
        with patch.object(subject.Expression, 'evaluate', return_value=True):
            with self.assertRaises(ValidationError):
                run(lo='3', hi='3', search_min='3', search_max='3')

    def test_boundary_probes_are_labeled_and_stay_in_search_domain(self):
        p = subject.propose(claim(), '1/10', '19/10', '7/10')
        for point in p['plan']['boundary_probes']:
            self.assertGreaterEqual(Fraction(point), Fraction(1, 10))
            self.assertLessEqual(Fraction(point), Fraction(19, 10))
        self.assertIn('boundary probes', p['plan']['method'])

    @unittest.skipUnless(shutil.which('node'), 'Node required only for frontend race simulation')
    def test_frontend_deferred_fetch_does_not_overwrite_new_draft(self):
        first = run()
        second = run(hi='2')
        fixtures = {'first': first, 'second': second}
        script = r'''
const vm=require('node:vm'), fs=require('node:fs'), assert=require('node:assert/strict');
const fixtures=JSON.parse(fs.readFileSync(0,'utf8')), elements=new Map(), requests=[];
function element(){return {value:'',checked:false,disabled:false,hidden:true,textContent:'',children:[],listeners:{},
  append(...xs){this.children.push(...xs)},replaceChildren(...xs){this.children=xs},
  addEventListener(k,f){this.listeners[k]=f},setAttribute(){},focus(){}}}
function get(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)}
const ctx=vm.createContext({document:{getElementById:get,createElement:element,createTextNode:s=>s},
  crypto:require('node:crypto').webcrypto,TextEncoder,Uint8Array,Blob,URL,setTimeout,
  fetch:(url,opts)=>new Promise(resolve=>requests.push({url,opts,resolve}))});
vm.runInContext(fs.readFileSync('static/app.js','utf8'),ctx);
function state(expr){return vm.runInContext(expr,ctx)}
function respond(request,body){request.resolve({ok:true,json:async()=>body})}
async function main(){
  get('claim').value=fixtures.first.proposal.raw_claim;
  get('search-min').value='0';get('search-max').value='3';get('step').value='1/4';
  const older=get('compile').onclick();
  get('claim').value=fixtures.second.proposal.raw_claim;get('claim').listeners.input();
  const newer=get('compile').onclick();
  respond(requests[1],{proposal:fixtures.second.proposal});await newer;
  respond(requests[0],{proposal:fixtures.first.proposal});await older;
  assert.equal(state('proposal.digest'),fixtures.second.proposal.digest,'late compile replaced newer proposal');
  get('confirmed').checked=true;get('confirmed').onchange();
  const pending=get('run').onclick();
  get('claim').value='unsupported new draft';get('claim').listeners.input();
  respond(requests[2],{report:fixtures.second,markdown:'saved report'});await pending;
  assert.equal(get('claim').value,'unsupported new draft');
  assert.equal(state('proposal'),null);assert.equal(get('confirmed').checked,false);
  assert.equal(get('results').hidden,true);assert.equal(state('history.length'),1);
  assert.equal(state('history[0].report.review_id'),fixtures.second.review_id);
  assert.equal(state('selected'),null);assert.equal(get('run').disabled,true);
  state('revise(history[0])');
  assert.equal(state('parent.review_id'),fixtures.second.review_id);
  get('new').onclick();
  assert.equal(state('parent'),null);assert.equal(state('history.length'),1);
  get('claim').value=fixtures.first.proposal.raw_claim;
  const compileAgain=get('compile').onclick();
  respond(requests[3],{proposal:fixtures.first.proposal});await compileAgain;
  get('confirmed').checked=true;get('confirmed').onchange();
  const swapped=get('run').onclick();
  respond(requests[4],{report:fixtures.second,markdown:'wrong proposal report'});await swapped;
  assert.equal(state('history.length'),1,'unbound response was accepted');
  assert.match(get('error').textContent,/not bound/);
  const forged=get('run').onclick();
  const corrupted=JSON.parse(JSON.stringify(fixtures.first));corrupted.review_id='forged-hash';
  respond(requests[5],{report:corrupted,markdown:'bad fingerprint'});await forged;
  assert.equal(state('history.length'),1,'bad fingerprint was archived');
  assert.match(get('error').textContent,/fingerprint mismatch/);
  process.stdout.write('PASS: stale compile, stale review, history isolation and response binding');
}
main().catch(e=>{console.error(e);process.exitCode=1});
'''
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(['node', '-e', script], input=json.dumps(fixtures),
                                text=True, capture_output=True, cwd=root, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)


if __name__ == '__main__':
    unittest.main()
