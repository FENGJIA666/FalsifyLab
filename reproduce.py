"""Replay a saved generic or revision-linked review. No network required."""
import json
import sys
from pathlib import Path
from falsifylab import search
from review import replay_report

if __name__ == '__main__':
    try:
        saved = json.loads(Path(sys.argv[1]).read_text())
        if saved.get('schema_version') == 2:
            fresh = replay_report(saved)
            label = fresh['review_id']
        else:
            fresh = search(saved['spec'])
            if fresh != saved:
                raise ValueError('Report, specification, or loaded engine differs.')
            label = fresh['status'] + ' ' + fresh['spec_sha256']
        print('REPRODUCED:', label)
    except (ValueError, KeyError, IndexError) as exc:
        print('MISMATCH:', exc)
        sys.exit(1)
