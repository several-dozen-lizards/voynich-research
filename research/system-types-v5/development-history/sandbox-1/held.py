"""Held statistics are inaccessible without a valid, complete claim freeze."""
from pathlib import Path
import json
from core import sha

class ClaimLocked(RuntimeError):
    pass

def require_freeze(root):
    root = Path(root).resolve()
    freeze_path = root / 'FREEZE.json'
    if not freeze_path.is_file():
        raise ClaimLocked('S_held locked: FREEZE.json does not exist')
    freeze = json.loads(freeze_path.read_text(encoding='utf-8'))
    if freeze.get('tier') != 'claim' or not freeze.get('definitions_complete'):
        raise ClaimLocked('incomplete or non-claim freeze')
    for required in ('PROTOCOL.json', 'MAPPING.json', 'held.py', 'core.py', 'GENERATORS/__init__.py'):
        if required not in freeze.get('files', {}):
            raise ClaimLocked('freeze omits required owner: ' + required)
    for name, expected in freeze['files'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or sha(path) != expected:
            raise ClaimLocked('freeze hash mismatch: ' + name)
    return freeze

def score(root, statistic, rows):
    require_freeze(root)
    # Dispatch stays closed until exact legacy definitions and control gates exist.
    raise NotImplementedError(f'{statistic}: claim method not yet qualified; no surrogate score is returned')
