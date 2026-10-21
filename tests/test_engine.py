import copy
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from falsifylab import ENGINE_SHA256, Expression, ValidationError, search, markdown, rational

CASES = json.loads((Path(__file__).resolve().parents[1]/'examples/cases.json').read_text())

def case(index=0):
    s = copy.deepcopy(CASES[index]); s['confirmed'] = True
    return s

class EngineTests(unittest.TestCase):
    def test_square_exact_witness(self):
        r = search(case())
        self.assertEqual(r['counts'], dict(grid_points=21,excluded=0,tested=21,undefined=0,violations=9))
        self.assertEqual(r['witnesses'][0]['assignment'], {'x':'1/10'})
        self.assertEqual(r['witnesses'][0]['comparisons'][0]['values'], ['1/100','1/10'])

    def test_integer_grid_is_not_proof(self):
        s=case();s['variables'][0]['step']='1'
        r=search(s)
        self.assertEqual(r['status'],'no_counterexample_in_grid')
        self.assertIn('not a proof',r['conclusion'])

    def test_euler_boundary_and_repair(self):
        s=case(1);r=search(s)
        self.assertEqual(r['witnesses'][0]['assignment'],{'h':'9/4'})
        self.assertEqual(r['counts']['violations'],4)
        s['assumptions']='0 < h <= 2'
        self.assertEqual(search(s)['status'],'no_counterexample_in_grid')

    def test_two_variables(self):
        r=search(case(2));self.assertEqual(r['counts']['tested'],81)
        self.assertEqual(r['counts']['violations'],0)

    def test_short_circuit_trace_does_not_double_count(self):
        s=case();s['assertion']='x != 0 and 1/x > 0'
        r=search(s)
        self.assertEqual(r['counts']['tested'],21)
        self.assertEqual(r['counts']['violations'],1)
        self.assertEqual(r['counts']['undefined'],0)
        self.assertIsNone(r['witnesses'][0]['comparisons'][1]['holds'])

    def test_confirmation_required(self):
        s=case();s['confirmed']=False
        with self.assertRaises(ValidationError):search(s)

    def test_undefined_not_counterexample(self):
        s=case();s['assertion']='1/x > 0'
        r=search(s);self.assertEqual(r['status'],'inconclusive')
        self.assertEqual(r['counts']['undefined'],1)
        self.assertEqual(r['counts']['violations'],0)

    def test_empty_domain(self):
        s=case();s['assumptions']='x > 5'
        self.assertEqual(search(s)['status'],'empty_domain')

    def test_exact_decimal(self):
        self.assertTrue(Expression('0.1 + 0.2 == 0.3',[],True).evaluate({}))

    def test_reject_execution_and_large_powers(self):
        for expression in ['__import__("os").system("id") == 0','x.__class__ == 1','[x] == [x]','x**999 >= 0','x**x >= 0','True == 1','x','x ^ 2 == 1']:
            with self.subTest(expression=expression),self.assertRaises(ValidationError):
                Expression(expression,['x'],True)

    def test_limits_and_bad_inputs(self):
        for mutation in [ {'variables':[]}, {'variables':[{'name':'x','min':'0','max':'2','step':'0'}]},
                         {'variables':[{'name':'x','min':'0','max':'100000','step':'1'}]},
                         {'assumptions':42}, {'claim':''}, {'variables':[{'name':'abs','min':'0','max':'2','step':'1'}]} ]:
            s=case();s.update(mutation)
            with self.subTest(mutation=mutation),self.assertRaises(ValidationError):search(s)

    def test_reproducibility_and_report(self):
        r=search(case());self.assertEqual(r,search(r['spec']))
        self.assertIn(r['spec_sha256'],markdown(r))
        s=case();s['assertion']='x**2 >= 0'
        self.assertNotEqual(r['spec_sha256'],search(s)['spec_sha256'])

    def test_nondivisible_upper_bound(self):
        s=case();s['variables'][0].update(max='1',step='3/10')
        self.assertEqual(search(s)['counts']['grid_points'],4)

    def test_short_circuit_domain_guard(self):
        s=case();s['assumptions']='x != 0 and 1/x > 0'
        r=search(s);self.assertEqual(r['counts']['undefined'],0)

    def test_chained_trace_records_false_comparison_before_undefined(self):
        s=case();s['variables'][0].update(min='0',max='0')
        s['assertion']='x < 0 < 1/x'
        r=search(s)
        self.assertEqual(r['counts']['violations'],1)
        self.assertEqual(r['counts']['undefined'],0)
        trace=r['witnesses'][0]['comparisons'][0]
        self.assertFalse(trace['holds'])
        self.assertEqual(trace['values'],['0','0'])
        self.assertEqual(trace['steps'],[{'left':'0','operator':'Lt','right':'0','holds':False}])
        self.assertEqual(trace['skipped_operands'],['1/x'])

    def test_nested_boolean_trace_never_evaluates_skipped_branch(self):
        s=case();s['variables'][0].update(min='0',max='0')
        s['assertion']='(x == 0 or 1/x > 1) and x > 1'
        r=search(s)
        self.assertEqual(r['counts']['violations'],1)
        trace=r['witnesses'][0]['comparisons']
        self.assertEqual([item['holds'] for item in trace],[True,None,False])
        self.assertTrue(trace[1]['skipped'])
        self.assertEqual(trace[1]['values'],[])

    def test_numeric_format_rejected_before_fraction_construction(self):
        for value in ['1e999999999','1e-999999999','1E6','1_000','0x10','nan','inf']:
            with self.subTest(value=value),patch('falsifylab.Fraction') as constructor:
                with self.assertRaises(ValidationError):rational(value)
                constructor.assert_not_called()
        with self.assertRaises(ValidationError):Expression('1e999999999 > x',['x'],True)

    def test_plain_numeric_formats_still_supported(self):
        for value,expected in [('0.125','1/8'),('.5','1/2'),('-3/4','-3/4'),('2.','2'),(' +2 ','2')]:
            with self.subTest(value=value):self.assertEqual(str(rational(value)),expected)

    def test_report_uses_loaded_source_fingerprint(self):
        with patch('falsifylab.Path.read_bytes',side_effect=AssertionError('must not reread changed source')):
            r=search(case())
        self.assertEqual(r['engine_sha256'],ENGINE_SHA256)
        self.assertEqual(r['engine_version'],'0.2.0')

if __name__=='__main__':unittest.main()
