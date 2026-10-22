# FalsifyLab — auditable Euler review

Review ID: 6f7ed0147177c5067b0e70ff8d541c2d6cb774cbff1be7abf27f817a9ff1615a

## Previous review (preserved)
Explicit Euler for y' = -rate*y with rate = 1 does not increase squared amplitude for every real initial y and every h in [0, 3].
Review ID: 2ae1687745aef3b66b3b8522801e91fc75d48041e8d01ffc65ed19f68fffe715
Confirmed proposal: 7a089870e34d4d106127998919a99aa562a435d16441c08c762f3e3dc42ff5d3
Claim domain: {"h_min": "0", "h_max": "3"}
Search plan: {"search_min": "0", "search_max": "3", "step": "1/4", "grid_points": 13, "boundary_probes": ["0", "1", "7/4", "2", "9/4", "3"], "budget": 10000, "method": "Exact rational grid plus theory-guided boundary probes within the search interval.", "rationale": "Probe zero, zero amplification, the non-expansion threshold 2/rate and its two sides.", "outside_claim_policy": "Record points beyond the claim interval as exploration."}
Grid outcome: counterexample_found
Counts: {"evaluated": 13, "in_claim": 13, "violations": 4, "outside_claim": 0, "outside_violations": 0}
Grid witnesses: [{"rate": "1", "h": "9/4", "initial_y": "1", "next_y": "-5/4", "squared_before": "1", "squared_after": "25/16", "squared_difference": "9/16"}, {"rate": "1", "h": "5/2", "initial_y": "1", "next_y": "-3/2", "squared_before": "1", "squared_after": "9/4", "squared_difference": "5/4"}, {"rate": "1", "h": "11/4", "initial_y": "1", "next_y": "-7/4", "squared_before": "1", "squared_after": "49/16", "squared_difference": "33/16"}, {"rate": "1", "h": "3", "initial_y": "1", "next_y": "-2", "squared_before": "1", "squared_after": "4", "squared_difference": "3"}]
Outside-domain exploration: []
Analytical outcome: refuted_by_analytic_witness
Analytical coverage: entire confirmed closed claim interval
y_next=(1-rate*h)y; y_next²-y²=rate*h*(rate*h-2)*y². With rate>0 and h>=0 this is nonpositive for all real y exactly when rate*h<=2.
Analytical witness: {"rate": "1", "h": "3", "initial_y": "1", "next_y": "-2", "squared_before": "1", "squared_after": "4", "squared_difference": "3"}
At rate*h=2, amplitude is preserved while the sign alternates.

## Current review
Explicit Euler for y' = -rate*y with rate = 1 does not increase squared amplitude for every real initial y and every h in [0, 2].
Review ID: 6f7ed0147177c5067b0e70ff8d541c2d6cb774cbff1be7abf27f817a9ff1615a
Confirmed proposal: d65c9f03a80e1b11a916d5ead352e8cd364f8b5716f363892aca67c8db3e2977
Claim domain: {"h_min": "0", "h_max": "2"}
Search plan: {"search_min": "0", "search_max": "3", "step": "1/4", "grid_points": 13, "boundary_probes": ["0", "1", "7/4", "2", "9/4", "3"], "budget": 10000, "method": "Exact rational grid plus theory-guided boundary probes within the search interval.", "rationale": "Probe zero, zero amplification, the non-expansion threshold 2/rate and its two sides.", "outside_claim_policy": "Record points beyond the claim interval as exploration."}
Grid outcome: no_counterexample_in_searched_points
Counts: {"evaluated": 13, "in_claim": 9, "violations": 0, "outside_claim": 4, "outside_violations": 4}
Grid witnesses: []
Outside-domain exploration: [{"rate": "1", "h": "9/4", "initial_y": "1", "next_y": "-5/4", "squared_before": "1", "squared_after": "25/16", "squared_difference": "9/16"}, {"rate": "1", "h": "5/2", "initial_y": "1", "next_y": "-3/2", "squared_before": "1", "squared_after": "9/4", "squared_difference": "5/4"}, {"rate": "1", "h": "11/4", "initial_y": "1", "next_y": "-7/4", "squared_before": "1", "squared_after": "49/16", "squared_difference": "33/16"}, {"rate": "1", "h": "3", "initial_y": "1", "next_y": "-2", "squared_before": "1", "squared_after": "4", "squared_difference": "3"}]
Analytical outcome: supported_by_analytic_condition
Analytical coverage: entire confirmed closed claim interval
y_next=(1-rate*h)y; y_next²-y²=rate*h*(rate*h-2)*y². With rate>0 and h>=0 this is nonpositive for all real y exactly when rate*h<=2.
Analytical witness: null
At rate*h=2, amplitude is preserved while the sign alternates.

## Evidence record
- Exact rational witnesses connect each result to a concrete assignment.
- Sampled search and analytical coverage are recorded alongside the confirmed claim.
- Revisions preserve the original review and its evidence.
- Source fingerprints and saved plans support deterministic replay.

## Reproduce
python3 reproduce.py report.json
Loaded source fingerprints: {"review": "bf6c9e2990196ebe91bec8f32a8d1595cb93a6efc2c2aed04cd9f0a978fd23e4", "engine": "eac14988c764e965c71c2110de3c237b59d5c2add080fcea23ec4e1b5a5b3ffc"}
