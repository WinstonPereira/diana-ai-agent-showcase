"""
SNIPPET ILUSTRATIVO — Pipeline de edição segura de código (auto-modificação).

NÃO é o código real da DIANA. É um exemplo genérico do padrão de engenharia
que permite uma IA editar o próprio código sem quebrar o sistema:

    1. Validação de sintaxe (AST) ANTES de gravar
    2. Checagem de nomes indefinidos (pyflakes) — pega funções removidas
       com chamadas órfãs, que é o bug clássico de auto-modificação
    3. Backup automático do arquivo original
    4. Teste real (import do módulo) APÓS gravar
    5. Rollback automático se o teste falhar

Este é o padrão "escreve com rede de segurança".
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
    """Roda pyflakes no arquivo e retorna nomes indefinidos."""
    try:
        proc = subprocess.run(
            ["python", "-m", "pyflakes", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return [ln for ln in proc.stdout.splitlines() if "undefined name" in ln]
    except Exception:
        return []  # pyflakes indisponível → não bloqueia


def _module_imports(path: Path) -> tuple[bool, str]:
    """Teste real: tenta importar o módulo."""
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
    """Escreve o arquivo só se passar em todas as validações."""

    # 1. Sintaxe
    ok, err = _syntax_ok(new_source)
    if not ok:
        return EditOutcome(False, str(path), f"Rejeitado — {err}")

    # 2. Backup do original (se existir)
    backup = path.with_suffix(path.suffix + ".bak")
    if path.exists():
        shutil.copy2(path, backup)

    # 3. Grava
    path.write_text(new_source, encoding="utf-8")

    # 4. Nomes indefinidos
    undef = _undefined_names(path)
    if undef:
        if path.exists() and backup.exists():
            shutil.copy2(backup, path)  # rollback
        return EditOutcome(False, str(path), f"Rejeitado — {undef[0]}")

    # 5. Teste real (só para .py)
    if path.suffix == ".py":
        imported, stderr = _module_imports(path)
        if not imported:
            if backup.exists():
                shutil.copy2(backup, path)  # rollback
            return EditOutcome(False, str(path), f"Revertido — {stderr}")

    return EditOutcome(True, str(path), "Edição aplicada e validada.")
