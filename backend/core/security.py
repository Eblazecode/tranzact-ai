from pathlib import Path
import re


SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_user_name(user_name: str) -> str:
    clean = SAFE_FILENAME_PATTERN.sub("_", user_name.strip())
    return clean.strip("_")


def ensure_within_directory(base_dir: Path, target: Path) -> Path:
    resolved_base = base_dir.resolve()
    resolved_target = target.resolve()
    if resolved_base not in resolved_target.parents and resolved_target != resolved_base:
        raise ValueError("Resolved path escaped the configured data directory.")
    return resolved_target
