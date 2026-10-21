# FalsifyLab

FalsifyLab is a local review workspace for computational-science researchers and students checking numerical-model claims. It makes assumptions, exact counterexamples and search limits visible, while preserving the original failure when a claim is revised.

## Focused workflow

For explicit Euler applied to scalar decay, y' = -rate*y with rate > 0, the question is whether one step avoids increasing squared amplitude for every real initial value throughout a closed nonnegative step interval. A strict controlled-English grammar extracts the rate and interval; unsupported prose is rejected. The user confirms the model, quantifier, assumptions, claim domain and separate search plan before execution.

## Demonstrated evidence

At rate = 1 and grid step = 1/4, the workflow distinguishes three situations. Counts below are exact rational evaluations; the full-domain analytical check is reported separately.

| Confirmed claim / search | Grid evidence | Full-domain check |
| --- | --- | --- |
| Claim [0,3]; search [0,1] | 5 pass; limited coverage | Refuted at h = 3 |
| Claim [0,3]; search [0,3] | 13 points; 4 violations | Refuted at h = 3 |
| Revised [0,2]; search [0,3] | 9 pass; 4 outside failures | Non-expansion holds |

For the full search, h = 9/4 and initial y = 1 give y_next = -5/4: squared amplitude rises from 1 to 25/16. Failures outside the revised domain are exploration, not counterexamples to it. The parent review remains intact.

## Hackathon contribution

Built during October 21-22, 2026: a local rational-search workbench, followed by the focused Euler workflow with confirmed interpretations, separate claim/search domains, preserved revisions and replayable evidence. The demonstrated contribution is this auditable review workflow. The scalar-decay model, Euler method and non-expansion condition are established mathematics, not new discoveries. Potential uses include teaching numerical stability and checking assumptions before extending a simulation; time savings and comparative benefits have not been measured.

## Evidence and limits

For this scalar model, non-expansion holds exactly when 0 <= rate*h <= 2. At the upper boundary, sign alternates and amplitude is unchanged; this is not strict decay. A passing rational grid is not proof and cannot hit isolated irrational counterexamples. JSON/Markdown reports retain the confirmed input, exact evidence, source fingerprints and revision chain; saved browser reports replay locally. Hashes check consistency, not human identity or approval.

The prototype runs locally with Python and a browser, without external service credentials. It supports only the documented claim grammar, is not a general theorem prover, and does not perform physical experiments or establish model validity. Submission status is tracked separately.
