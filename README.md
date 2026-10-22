# FalsifyLab

Turn mathematical claims into exact, replayable evidence. Built for OSI Hackathon 2026, FalsifyLab connects claim interpretation, exact counterexample search, mathematical checks and revision history in one workspace. Its Euler demonstration follows a numerical claim through to a reproducible result.

## Run

Use Python 3.10+ and a browser. From this directory:

```sh
python3 server.py
```

Open http://127.0.0.1:8765 . To select another port, run `python3 server.py --port 8767`. The mathematical workbench is at `/sandbox`.

## See the achievements

1. Keep the displayed Euler claim with rate 1 and `h` in `[0,3]`; compile, inspect, confirm and run. Inspect the exact counterexample: `h=9/4` and `y=1` give `y_next=-5/4` and squared amplitude `25/16`.
2. Revise the claim to `[0,2]` and run the review. The workspace connects the revised result to its original investigation and preserves the evidence history.
3. Inspect the mathematical check: at `h=3` and `y=1`, it computes `y_next=-2` and squared amplitude `4`. The search and mathematical analysis provide complementary evidence.
4. Export JSON or Markdown. Replay JSON with `python3 reproduce.py path/to/report.json`.

Reports retain the claim, plan, exact values, source fingerprints and revision history. Export JSON to carry your investigation between sessions.

## Verify

Run the engine and browser-script checks with Python and Node.js (`node`):

```sh
python3 -m unittest discover -s tests -v
python3 reproduce.py evidence/v5-browser-original.json
python3 reproduce.py evidence/v5-browser-revision.json
python3 reproduce.py evidence/v5-browser-partial.json
```

The project has passed 42 tests and report replay, with independent arithmetic checks and browser workflow checks.

## Hackathon achievements

Built during October 21-22, 2026: a rational-search workbench and an integrated review workflow combining claim interpretation, exact counterexamples, mathematical checks, traceable revisions and replayable reports.

Designed for scientific-computing learners and developers reviewing simulation assumptions. See [hackathon contribution](docs/CONTRIBUTION.md) and [one-page description](docs/ONE_PAGE_CONTENT.md).

The application uses Python's standard library and a browser. Node runs the frontend tests.
