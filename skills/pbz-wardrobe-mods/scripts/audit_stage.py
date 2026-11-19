#!/usr/bin/env python3
"""Read-only PBZ add/repair stage audit. Only an explicit external report is written."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def relative_name(value):
    if not isinstance(value, str) or not value:
        raise ValueError('Manifest relative path must be a nonempty string')
    parts = value.replace('\\', '/').split('/')
    win = PureWindowsPath(value)
    if win.drive or win.root or any(p in ('', '.', '..') or ':' in p or
                                    p.endswith((' ', '.')) for p in parts):
        raise ValueError('Unsafe relative path: ' + value)
    return '/'.join(parts)


def contained(root, name):
    path = root.joinpath(*name.split('/'))
    if not path.resolve().is_relative_to(root):
        raise ValueError('Path escapes root: ' + str(path))
    return path


def read_manifest(path):
    raw = path.read_bytes()
    data = json.loads(raw.decode('utf-16' if raw[:2] in (b'\xff\xfe', b'\xfe\xff')
                                 else 'utf-8-sig'))
    if not isinstance(data, list):
        raise ValueError('Baseline must be a list of {relative, sha256} records')
    result = {}
    for item in data:
        if not isinstance(item, dict):
            raise ValueError('Invalid baseline record')
        name = relative_name(item.get('relative'))
        sha = item.get('sha256', '')
        if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', sha):
            raise ValueError('Invalid SHA-256: ' + name)
        key = name.casefold()
        if key in result:
            raise ValueError('Duplicate/case-colliding baseline path: ' + name)
        result[key] = {'relative': name, 'sha256': sha.lower()}
    return result


def staged_files(root):
    result = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            p = Path(folder) / name
            # Reject nested links/junctions: os.walk may otherwise silently omit them.
            if p.is_symlink() or p.resolve() != p.absolute():
                raise ValueError('Linked stage directory requires manual review: ' + str(p))
        for name in files:
            p = Path(folder) / name
            rel = relative_name(p.relative_to(root).as_posix())
            contained(root, rel)
            if p.is_symlink():
                raise ValueError('Linked stage file requires manual review: ' + rel)
            key = rel.casefold()
            if key in result:
                raise ValueError('Case-colliding staged file: ' + rel)
            result[key] = {'relative': rel, 'path': p, 'sha256': digest(p)}
    if not result:
        raise ValueError('Stage is empty')
    return result


def audit(baseline, game, stage):
    game, stage = Path(game).resolve(), Path(stage).resolve()
    if not game.is_dir() or not stage.is_dir():
        raise ValueError('Game and stage must be existing directories')
    if game.is_relative_to(stage) or stage.is_relative_to(game):
        raise ValueError('Game and stage must be separate trees')
    old, new = read_manifest(Path(baseline)), staged_files(stage)
    blockers, writes = [], []
    for key, row in old.items():
        target = contained(game, row['relative'])
        if not target.is_file():
            blockers.append({'kind': 'missing_live_baseline', 'relative': row['relative']})
        elif digest(target) != row['sha256']:
            blockers.append({'kind': 'live_baseline_drift', 'relative': row['relative']})
        if key not in new:
            blockers.append({'kind': 'missing_from_full_stage', 'relative': row['relative']})
    for key, row in new.items():
        target = contained(game, row['relative'])
        if key not in old and target.exists():
            blockers.append({'kind': 'unmanaged_target_collision', 'relative': row['relative']})
        if key not in old or row['sha256'] != old[key]['sha256']:
            writes.append({'relative': row['relative'], 'action': 'add' if key not in old else 'replace',
                           'before': old[key]['sha256'] if key in old else None,
                           'after': row['sha256']})
    return {'ok': not blockers, 'game': str(game), 'stage': str(stage),
            'baselineFiles': len(old), 'stageFiles': len(new),
            'blockers': blockers, 'plannedWrites': writes,
            'limits': 'File baseline only; no mutation, backup, table, rig, voice or runtime validation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--stage', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.baseline, args.game, args.stage)
        if args.report:
            report = args.report.resolve()
            if (report == args.baseline.resolve() or
                    any(report.is_relative_to(p.resolve()) for p in (args.game, args.stage))):
                raise ValueError('Report must be outside the game/stage and must not overwrite the baseline')
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['ok'] else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Audit input error: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
