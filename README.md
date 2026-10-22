# FalsifyLab

Turn numerical-model claims into exact, replayable evidence. Built for OSI Hackathon 2026, FalsifyLab connects confirmed assumptions, counterexample search and preserved revisions in one local workspace. It reviews one-step squared-amplitude non-expansion for explicit Euler applied to the normalized scalar model `y′ = -rate*y`. The application runs with Python and a browser, without external service credentials.

## Run

Python 3.10+ and a modern browser are sufficient for the application. From this directory:

```sh
python3 server.py
```

Open http://127.0.0.1:8765 . The server binds only to loopback. If that port is busy, use `python3 server.py --port 8767`. The manual mathematical workbench is at `/sandbox`.

## Demonstrate

1. Keep the displayed claim with rate 1 and `h` in `[0,3]`; compile, inspect, confirm and run. The full search evaluates 13 points and finds four violations; `h=9/4`, `y=1` gives `y_next=-5/4`, squared amplitude `25/16`.
2. Revise the claim to `[0,2]`, leaving search `[0,3]`. Nine in-domain points pass and four failing outside-domain points are exploration; the original failure remains in the parent review.
3. Start a new investigation with claim `[0,3]` but search only `[0,1]`. The finite search passes, while separate full-domain analysis refutes at `h=3`.
4. Save JSON or Markdown. Replay JSON with `python3 reproduce.py path/to/report.json`.

The workflow displays finite-search evidence alongside the full-domain scalar Euler condition `0 <= rate*h <= 2`. At the upper boundary, amplitude is preserved. Reports keep the parent chain, confirmed plan and source fingerprints for consistency checking and replay. Export JSON to retain session history across browser sessions.

## Verify

Python runs the engine tests; the adversarial suite additionally needs Node.js available as `node` for browser-script checks.

```sh
python3 -m unittest discover -s tests -v
python3 reproduce.py evidence/browser-original.json
python3 reproduce.py evidence/browser-revision.json
python3 reproduce.py evidence/browser-partial.json
```

The local review passed 42 saved tests and report replay, with independent arithmetic checks and actual browser acceptance. 

## Hackathon achievements

Built during October 21-22, 2026: a rational-search workbench and an integrated review workflow combining confirmed interpretation, exact counterexamples, separate claim/search domains, retained revisions and replayable reports. The demonstration builds on established Euler mathematics to make numerical assumptions inspectable and results reproducible.

Designed for scientific-computing learners and developers reviewing simulation assumptions. See [hackathon contribution](docs/CONTRIBUTION.md) and [one-page description](docs/ONE_PAGE_CONTENT.md).

The application uses Python's standard library and runs locally with a browser. Node is used for frontend tests.
