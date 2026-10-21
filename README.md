# FalsifyLab

A local, auditable mathematical-claim review prototype for OSI Hackathon 2026. It reviews one-step squared-amplitude non-expansion for explicit Euler applied to the normalized scalar model `y′ = -rate*y`. The application runs with Python and a browser, without external service credentials.

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

A passing rational grid is not proof. Under this model's stated assumptions, the known condition is `0 <= rate*h <= 2`; at the upper boundary amplitude is preserved, not strictly decaying. Unsupported prose is rejected. Session history lives in the tab; export before closing it. Reports keep the parent chain, confirmed plan and source fingerprints. Hashes detect inconsistencies but do not authenticate human approval. Trace samples are capped at 120 and witness examples at five; total counts and replay cover the full finite run.

## Verify

Python runs the engine tests; the adversarial suite additionally needs Node.js available as `node` for browser-script checks.

```sh
python3 -m unittest discover -s tests -v
python3 reproduce.py evidence/browser-original.json
python3 reproduce.py evidence/browser-revision.json
python3 reproduce.py evidence/browser-partial.json
```

The local review passed 42 saved tests and report replay, with independent arithmetic checks and actual browser acceptance. This supports the declared scope, not correctness for arbitrary models.

## Contribution and limits

Built during October 21–22, 2026: a rational-search workbench and focused review workflow combining confirmation, coverage separation, retained revisions and replay. Euler mathematics is established background. Intended users are scientific-computing learners and developers checking assumptions. No research time savings, experimental results, first-of-its-kind capability or superiority are claimed. See [contribution](docs/CONTRIBUTION.md) and [one-page description](docs/ONE_PAGE_CONTENT.md).

The delivered application uses Python's standard library; Node is a test dependency only. No Valency, Adaption or marimo integration is present. Submission status is tracked separately.
