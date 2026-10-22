# FalsifyLab

Turn mathematical claims into exact, replayable evidence. Built for OSI Hackathon 2026, FalsifyLab connects claim interpretation, exact counterexample search, mathematical checks and revision history in one workspace. Its Euler demonstration follows a numerical claim through to a reproducible result.

## Run

Use Python 3.10+ and a browser. From this directory:

```sh
python3 server.py
```

Open http://127.0.0.1:8765 . To select another port, run `python3 server.py --port 8767`. The mathematical workbench is at `/sandbox`.

## See the achievements

1. Keep the displayed claim with rate 1 and `h` in `[0,3]`; compile, inspect, confirm and run. The search evaluates 13 points and identifies four counterexamples. For `h=9/4` and `y=1`, it finds `y_next=-5/4` and squared amplitude `25/16`.
2. Revise the claim to `[0,2]`, retaining search `[0,3]`. Nine in-domain points pass, four exploratory results remain visible, and the evidence history stays connected to the revised claim.
3. Start an investigation with claim `[0,3]` and search `[0,1]`. Five sampled points pass; the mathematical check identifies a counterexample at `h=3`.
4. Export JSON or Markdown. Replay JSON with `python3 reproduce.py path/to/report.json`.

The Euler demonstration connects sampled results with the mathematical condition `0 <= rate*h <= 2`. Reports retain the claim, plan, evidence, source fingerprints and revision history. Export JSON to carry your investigation between sessions.

## Verify

Run the engine and browser-script checks with Python and Node.js (`node`):

```sh
python3 -m unittest discover -s tests -v
python3 reproduce.py evidence/v4-browser-original.json
python3 reproduce.py evidence/v4-browser-revision.json
python3 reproduce.py evidence/v4-browser-partial.json
```

The project has passed 42 tests and report replay, with independent arithmetic checks and browser workflow checks.

## Hackathon achievements

Built during October 21-22, 2026: a rational-search workbench and an integrated review workflow combining claim interpretation, exact counterexamples, mathematical checks, traceable revisions and replayable reports.

Designed for scientific-computing learners and developers reviewing simulation assumptions. See [hackathon contribution](docs/CONTRIBUTION.md) and [one-page description](docs/ONE_PAGE_CONTENT.md).

The application uses Python's standard library and a browser. Node runs the frontend tests.
