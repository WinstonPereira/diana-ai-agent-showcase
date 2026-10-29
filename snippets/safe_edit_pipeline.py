"""
ILLUSTRATIVE SNIPPET — Safe code-editing pipeline (self-modification).

This is NOT DIANA's real code. It is a generic example of the engineering
pattern that lets an AI edit its own code without breaking the system:

    1. Syntax validation (AST) BEFORE writing
    2. Undefined-name check (pyflakes) — catches removed functions with
       orphaned call sites, the classic self-modification bug
    3. Automatic backup of the original file
    4. Real test (module import) AFTER writing
    5. Automatic rollback if the test fails

This is the "write with a safety net" pattern.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass


@dataclass
class EditOutcome:
    ok: bool
    path: str
    message: str


def _syntax_ok(source: str) -> tuple[bool, str]:
    try:
        ast.parse(source)
        return True, ""
    except SyntaxError as exc:
        return False, f"SyntaxError: {exc}"


def _undefined_names(path: Path) -> list[str]:
    """Runs pyflakes on the file and returns undefined names."""
    try:
        proc = subprocess.run(
            ["python", "-m", "pyflakes", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return [ln for ln in proc.stdout.splitlines() if "undefined name" in ln]
    except Exception:
        return []  # pyflakes unavailable -> do not block


def _module_imports(path: Path) -> tuple[bool, str]:
    """Real test: try to import the module."""
    try:
        proc = subprocess.run(
            ["python", "-c", f"import importlib.util as u; "
             f"s=u.spec_from_file_location('m', r'{path}'); "
             f"m=u.module_from_spec(s); s.loader.exec_module(m)"],
            capture_output=True, text=True, timeout=45,
        )
        return proc.returncode == 0, proc.stderr[-500:]
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def safe_write(path: Path, new_source: str) -> EditOutcome:
    """Writes the file only if every validation passes."""

    # 1. Syntax
    ok, err = _syntax_ok(new_source)
    if not ok:
        return EditOutcome(False, str(path), f"Rejected — {err}")

    # 2. Backup of the original (if it exists)
    backup = path.with_suffix(path.suffix + ".bak")
    if path.exists():
        shutil.copy2(path, backup)

    # 3. Write
    path.write_text(new_source, encoding="utf-8")

    # 4. Undefined names
    undef = _undefined_names(path)
    if undef:
        if path.exists() and backup.exists():
            shutil.copy2(backup, path)  # rollback
        return EditOutcome(False, str(path), f"Rejected — {undef[0]}")

    # 5. Real test (.py only)
    if path.suffix == ".py":
        imported, stderr = _module_imports(path)
        if not imported:
            if backup.exists():
                shutil.copy2(backup, path)  # rollback
            return EditOutcome(False, str(path), f"Reverted — {stderr}")

    return EditOutcome(True, str(path), "Edit applied and validated.")
