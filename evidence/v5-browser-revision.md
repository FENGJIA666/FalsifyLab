# FalsifyLab — auditable Euler review

Review ID: 9b5d9efce884d70c82a975498f4bcc723144a217fb64c648719ac4485ea61feb

## Previous review (preserved)
Explicit Euler for y' = -rate*y with rate = 1 keeps squared amplitude at or below its initial value for every real initial y and every h in [0, 3].
Review ID: 16c509505c6af95fdbbfac1fd6f96ac4d3de07f85f307f42e98026788999a52d
Confirmed proposal: 5192531470c8db2eaeaa7312a63fd6b1d2541b130e1e5566b024ee51738e833e
Claim domain: {"h_min": "0", "h_max": "3"}
Search plan: {"search_min": "0", "search_max": "3", "step": "1/4", "grid_points": 13, "boundary_probes": ["0", "1", "7/4", "2", "9/4", "3"], "budget": 10000, "method": "Exact rational grid plus theory-guided boundary probes within the search interval.", "rationale": "Probe zero, zero amplification, the amplitude-preserving threshold 2/rate and its two sides.", "outside_claim_policy": "Record points beyond the claim interval as exploration."}
Search outcome: exact counterexample identified
Counts: {"evaluated": 13, "in_claim": 13, "violations": 4, "outside_claim": 0, "outside_violations": 0}
Grid witnesses: [{"rate": "1", "h": "9/4", "initial_y": "1", "next_y": "-5/4", "squared_before": "1", "squared_after": "25/16", "squared_difference": "9/16"}, {"rate": "1", "h": "5/2", "initial_y": "1", "next_y": "-3/2", "squared_before": "1", "squared_after": "9/4", "squared_difference": "5/4"}, {"rate": "1", "h": "11/4", "initial_y": "1", "next_y": "-7/4", "squared_before": "1", "squared_after": "49/16", "squared_difference": "33/16"}, {"rate": "1", "h": "3", "initial_y": "1", "next_y": "-2", "squared_before": "1", "squared_after": "4", "squared_difference": "3"}]
Outside-domain exploration: []
Mathematical analysis: exact counterexample identified
Analytical coverage: entire confirmed closed claim interval
y_next=(1-rate*h)y; y_next²-y²=rate*h*(rate*h-2)*y². For rate>0 and h>=0, y_next²<=y² for all real y exactly when rate*h<=2.
Analytical witness: {"rate": "1", "h": "3", "initial_y": "1", "next_y": "-2", "squared_before": "1", "squared_after": "4", "squared_difference": "3"}
At rate*h=2, amplitude is preserved while the sign alternates.

## Current review
Explicit Euler for y' = -rate*y with rate = 1 keeps squared amplitude at or below its initial value for every real initial y and every h in [0, 2].
Review ID: 9b5d9efce884d70c82a975498f4bcc723144a217fb64c648719ac4485ea61feb
Confirmed proposal: e976dac3571affa87c247433a38b35864bf2f679b211da19e5e84929a3d68a6b
Claim domain: {"h_min": "0", "h_max": "2"}
Search plan: {"search_min": "0", "search_max": "3", "step": "1/4", "grid_points": 13, "boundary_probes": ["0", "1", "7/4", "2", "9/4", "3"], "budget": 10000, "method": "Exact rational grid plus theory-guided boundary probes within the search interval.", "rationale": "Probe zero, zero amplification, the amplitude-preserving threshold 2/rate and its two sides.", "outside_claim_policy": "Record points beyond the claim interval as exploration."}
Search outcome: exact evaluations recorded
Counts: {"evaluated": 13, "in_claim": 9, "violations": 0, "outside_claim": 4, "outside_violations": 4}
Grid witnesses: []
Outside-domain exploration: [{"rate": "1", "h": "9/4", "initial_y": "1", "next_y": "-5/4", "squared_before": "1", "squared_after": "25/16", "squared_difference": "9/16"}, {"rate": "1", "h": "5/2", "initial_y": "1", "next_y": "-3/2", "squared_before": "1", "squared_after": "9/4", "squared_difference": "5/4"}, {"rate": "1", "h": "11/4", "initial_y": "1", "next_y": "-7/4", "squared_before": "1", "squared_after": "49/16", "squared_difference": "33/16"}, {"rate": "1", "h": "3", "initial_y": "1", "next_y": "-2", "squared_before": "1", "squared_after": "4", "squared_difference": "3"}]
Mathematical analysis: condition verified
Analytical coverage: entire confirmed closed claim interval
y_next=(1-rate*h)y; y_next²-y²=rate*h*(rate*h-2)*y². For rate>0 and h>=0, y_next²<=y² for all real y exactly when rate*h<=2.
Analytical witness: null
At rate*h=2, amplitude is preserved while the sign alternates.

## Evidence record
- Exact rational witnesses connect each result to a concrete assignment.
- Search coverage and mathematical analysis are recorded alongside the confirmed claim.
- Revisions preserve the original review and its evidence.
- Source fingerprints and saved plans support deterministic replay.

## Reproduce
python3 reproduce.py report.json
Loaded source fingerprints: {"review": "9046fe5229e818a796a94831feee75c81e250e5bb9ae64880f724e99c7b01f17", "engine": "454d35d6d711d80e37fd72c79ef4424c6e4551a0d5dc6c347d94286fecb60f82"}
