# FalsifyLab

Turn mathematical claims into exact, replayable evidence. FalsifyLab gives scientific-computing researchers and students a clear path from a numerical-model claim to a counterexample, a revised assumption and a reproducible review.

## The problem we solve

A simulation can pass every sampled test while its broader claim still fails. When assumptions change, the original evidence can also become disconnected from the revised conclusion. FalsifyLab connects the claim, its search coverage and its revision history in one review workspace.

## What we built

Built during the OSI Hackathon on October 21-22, 2026, FalsifyLab combines controlled-English claim interpretation, user-confirmed assumptions, exact rational search, full-domain analysis for scalar Euler non-expansion, preserved parent reviews and deterministic report replay. The application runs locally with Python and a browser.

## Demonstrated achievements

The working demonstration reviews explicit Euler for scalar decay, y' = -rate*y. At rate = 1 and grid step = 1/4, it produces three complementary results:

| Confirmed claim / search | Exact grid evidence | Full-domain result |
| --- | --- | --- |
| Claim [0,3]; search [0,1] | 5 sampled points pass | Finds failure at h = 3 |
| Claim [0,3]; search [0,3] | 13 points; 4 violations | Finds failure at h = 3 |
| Revised [0,2]; search [0,3] | 9 in-domain points pass | Non-expansion holds |

The full search finds the exact witness h = 9/4, y = 1: y_next = -5/4 and squared amplitude rises to 25/16. Revising the claim to [0,2] preserves the original review and classifies the four failing points above 2 as outside-domain exploration. The partial-search case demonstrates why the separate full-domain check matters.

## Evidence that travels with the result

JSON and Markdown exports retain the confirmed claim, search plan, exact evidence, source fingerprints and revision chain. Saved browser reports replay locally. The recorded validation includes 42 passing tests, independent arithmetic checks and browser workflow checks.

## Why it matters

FalsifyLab makes numerical assumptions inspectable and review results reproducible. Its contribution is a complete claim-to-evidence workflow: confirm the interpretation, expose a failing assumption, revise the claim and preserve the reasoning. It provides a practical workspace for teaching numerical stability and reviewing simulation assumptions.
