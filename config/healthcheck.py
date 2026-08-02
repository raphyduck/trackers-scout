#!/usr/bin/env python3
"""Healthcheck tracker-monitor : le scan a-t-il tourne dans la derniere heure ?
Remplace le one-liner du Dockerfile (ligne 33) qui etait un SyntaxError Python
(`if not state: exit(1);` compound statement dans un -c joint par des ';'),
donc echouait a 100% depuis la creation du conteneur."""
import json
import os
import sys
from datetime import datetime, timedelta

STATE = "/config/state.json"

if not os.path.exists(STATE):
    sys.exit(1)
try:
    with open(STATE) as fh:
        state = json.load(fh)
except (json.JSONDecodeError, OSError):
    sys.exit(1)
if not state:
    sys.exit(1)
checks = [
    datetime.fromisoformat(v["last_check"])
    for v in state.values()
    if isinstance(v, dict) and "last_check" in v
]
sys.exit(0 if checks and max(checks) > datetime.now() - timedelta(hours=1) else 1)
