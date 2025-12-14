#!/usr/bin/env python3
"""Create a snapshot backup of the current app state into backups/<phase_name>/"""
import os
import shutil
import sys
from datetime import datetime


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BACKUPS_DIR = os.path.join(REPO_ROOT, 'backups')


def safe_copy(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def lock_in_phase(phase_name: str):
    target = os.path.join(BACKUPS_DIR, phase_name)
    if os.path.exists(target):
        # create a timestamped sibling to avoid overwriting
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        target = f"{target}-{ts}"

    os.makedirs(target, exist_ok=True)

    items_to_copy = [
        'README.md', 'requirements.txt', 'requirements_strategies.txt', 'run_tests.sh',
        'src', 'static', 'templates', 'cache', 'scripts', 'backtest_tsls.py', 'backtest_tza.py'
    ]

    included = []
    for item in items_to_copy:
        src = os.path.join(REPO_ROOT, item)
        if os.path.exists(src):
            dst = os.path.join(target, item)
            try:
                safe_copy(src, dst)
                included.append(item)
            except Exception as e:
                print(f"Warning: failed to copy {item}: {e}")

    # Write PHASE_INFO.md
    info_path = os.path.join(target, 'PHASE_INFO.md')
    commit = None
    try:
        import subprocess
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT).decode().strip()
    except Exception:
        commit = 'unknown'

    with open(info_path, 'w') as f:
        f.write(f"# {phase_name}\n\n")
        f.write(f"Locked at: {datetime.utcnow().isoformat()} UTC\n\n")
        f.write(f"Git commit: {commit}\n\n")
        f.write("Included files and folders:\n")
        for it in included:
            f.write(f"- {it}\n")

    # Write PHASE_HISTORY.md (simple entry)
    history_path = os.path.join(target, 'PHASE_HISTORY.md')
    with open(history_path, 'w') as f:
        f.write(f"# Phase {phase_name}\n\nSnapshot created on {datetime.utcnow().isoformat()} UTC.\n")

    print(f"Locked in phase: {target}")
    return target


if __name__ == '__main__':
    if len(sys.argv) > 1:
        phase = sys.argv[1]
    else:
        phase = 'sixteenth-phase'
    lock_in_phase(phase)
