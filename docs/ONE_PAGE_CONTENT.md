# FalsifyLab

Turn mathematical claims into exact, replayable evidence. FalsifyLab connects a written claim, an exact counterexample and a traceable revision in one workspace for scientific-computing researchers and students.

## The problem we solve

Researchers need to connect numerical results with the assumptions behind them. FalsifyLab brings the claim, search results and revision history together, making each step easy to inspect, explain and reproduce.

## What we built

Built during the OSI Hackathon on October 21-22, 2026, FalsifyLab turns a written Euler claim into a reviewable plan, searches with exact fractions, checks the mathematics, preserves revisions and replays exported results. Researchers can follow the evidence from the first question to the refined conclusion.

## Demonstrated achievements

The demonstration reviews the Euler update for y' = -rate*y. At rate = 1 and grid step = 1/4, the workspace delivers three results:

| Claim / search interval | Search result | Mathematical check |
| --- | --- | --- |
| Claim [0,3]; search [0,1] | 5 sampled points pass | Counterexample at h = 3 |
| Claim [0,3]; search [0,3] | 13 points; 4 counterexamples | Counterexample at h = 3 |
| Revised [0,2]; search [0,3] | 9 in-domain points pass | Non-expansion holds |

FalsifyLab finds the exact witness h = 9/4, y = 1: y_next = -5/4 and squared amplitude rises to 25/16. The researcher then revises the claim to [0,2], keeping the evidence history and the four exploratory results above 2. The mathematical check also identifies h = 3 when the sampled search covers [0,1].

## Evidence that travels with the result

JSON and Markdown exports carry the claim, search plan, exact evidence and revision history. Saved browser reports replay through a single command. The project has passed 42 tests, independent arithmetic checks and browser workflow checks.

## Why it matters

FalsifyLab turns numerical review into a clear, reproducible process: inspect the assumptions, find exact counterexamples, refine the claim and share the reasoning. It brings numerical stability to life for learners and gives simulation developers a practical way to review their assumptions.
