#!/usr/bin/env python3
"""Shared manifest loading for repository instruction tools."""

import json
from pathlib import Path


def load_scopes(manifest_path: Path, cohort_root: Path):
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for repository in data["repositories"]:
        repository_path = cohort_root / repository["path"]
        for scope in repository.get("scopes", ["."]):
            yield (
                repository_path / scope,
                Path(repository["path"]) / scope,
                repository.get("deferred"),
            )


def first_active_line(text: str):
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return None
