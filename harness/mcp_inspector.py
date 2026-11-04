"""Anbindung an den MCP Inspector (CLI) mit Fallback auf mcp_client.py.

Der Inspector wird über ``npx -y @modelcontextprotocol/inspector@latest --cli``
gestartet. Er liefert JSON auf stdout und einen Exit-Code; bei ``tools/call``
mit ``isError`` ist der Exit-Code 5, das JSON bleibt aber gültig. Fehlt npx oder
ist Node älter als 22.19, sprechen wir das Protokoll direkt über ``mcp_client``.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

MIN_NODE = (22, 19)
TIMEOUT = 60.0
SCRATCH_TMP = Path.cwd() / "scratch" / "tmp"
FALLBACK_NOTE = "Inspector fehlt, Fallback"


class InspectorError(RuntimeError):
    """Aufruf des Inspectors fehlgeschlagen oder Ausgabe nicht lesbar."""


@dataclass
class InspectorResult:
    data: object
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    fallback: bool = False
    note: str = ""


@dataclass
class _Availability:
    ok: bool
    reason: str = ""


def _node_version(node: str) -> tuple[int, int]:
    try:
        result = subprocess.run(
            [node, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InspectorError(f"Node-Version nicht lesbar: {exc}") from exc
    match = re.search(r"v?(\d+)\.(\d+)", result.stdout)
    if result.returncode != 0 or match is None:
        raise InspectorError(
            "Node-Version nicht lesbar: " + (result.stderr.strip() or result.stdout.strip())
        )
    return int(match.group(1)), int(match.group(2))


def availability() -> _Availability:
    """Prüft npx und die von ihm benötigte Node-Version."""
    npx = shutil.which("npx")
    node = shutil.which("node")
    if not npx:
        return _Availability(False, "npx nicht im PATH")
    if not node:
        return _Availability(False, "node nicht im PATH")
    try:
        version = _node_version(node)
    except InspectorError as exc:
        return _Availability(False, str(exc))
    if version < MIN_NODE:
        return _Availability(
            False,
            f"Node {version[0]}.{version[1]} < {MIN_NODE[0]}.{MIN_NODE[1]}",
        )
    return _Availability(True, "")


def _scratch_dirs() -> tuple[Path, Path, Path]:
    tmp = SCRATCH_TMP / "inspector-tmp"
    cache = SCRATCH_TMP / "npm-cache"
    home = SCRATCH_TMP / "inspector-home"
    for path in (tmp, cache, home):
        path.mkdir(parents=True, exist_ok=True)
    return tmp, cache, home


def _inspector_env(server_env: dict[str, str]) -> dict[str, str]:
    tmp, cache, home = _scratch_dirs()
    env = dict(os.environ)
    env["TMPDIR"] = str(tmp)
    env["npm_config_cache"] = str(cache)
    env["npm_config_update_notifier"] = "false"
    env["NO_UPDATE_NOTIFIER"] = "1"
    env.setdefault("HOME", str(home))
    return env


def _parse_json(text: str) -> object:
    stripped = text.strip()
    if not stripped:
        raise InspectorError("Inspector lieferte kein JSON auf stdout")
    decoder = json.JSONDecoder()
    try:
        value, _end = decoder.raw_decode(stripped)
        return value
    except json.JSONDecodeError as exc:
        start = stripped.find("{")
        if start >= 0:
            try:
                value, _end = decoder.raw_decode(stripped[start:])
                return value
            except json.JSONDecodeError:
                pass
        raise InspectorError(f"Inspector-JSON nicht lesbar: {exc.msg}") from exc


def _run(
    server_command: list[str],
    env: dict[str, str],
    method_args: list[str],
) -> InspectorResult:
    npx = shutil.which("npx")
    if not npx:
        raise InspectorError("npx nicht im PATH")
    command = [
        npx,
        "-y",
        "@modelcontextprotocol/inspector@latest",
        "--cli",
        *[str(part) for part in server_command],
    ]
    for key, value in env.items():
        if str(value) == "":
            continue
        command.extend(["-e", f"{key}={value}"])
    command.extend(method_args)
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            env=_inspector_env(env),
        )
    except subprocess.TimeoutExpired as exc:
        raise InspectorError(f"Inspector-Timeout nach {TIMEOUT:.0f} s") from exc
    except OSError as exc:
        raise InspectorError(f"Inspector-Start fehlgeschlagen: {exc}") from exc
    try:
        data = _parse_json(completed.stdout)
    except InspectorError as exc:
        raise InspectorError(
            f"{exc}; stderr={completed.stderr.strip()[:500]!r}"
        ) from exc
    return InspectorResult(
        data=data,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def result_text(data: object) -> str:
    """Sichtbarer Text einer tools/call-Antwort (auch JSON-RPC-Fehler)."""
    if not isinstance(data, dict):
        return ""
    parts: list[str] = []
    error = data.get("error")
    if error:
        parts.append(json.dumps(error, ensure_ascii=False))
    content = data.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
    if data.get("isError"):
        parts.append("isError")
    return "\n".join(part for part in parts if part)


def result_is_error(data: object) -> bool:
    if not isinstance(data, dict):
        return False
    return bool(data.get("error")) or data.get("isError") is True


def _fallback_client(server_command: list[str], env: dict[str, str]):
    try:
        from mcp_client import DEFAULT_TIMEOUT, McpClient
    except ImportError:  # pragma: no cover - Paketimport
        from .mcp_client import DEFAULT_TIMEOUT, McpClient
    client = McpClient(timeout=DEFAULT_TIMEOUT)
    client.start(server_command, env)
    return client


def list_tools(server_command: list[str], env: dict[str, str]) -> InspectorResult:
    """``tools/list`` über den Inspector, sonst direkt über den MCP-Client."""
    state = availability()
    if state.ok:
        result = _run(server_command, env, ["--method", "tools/list"])
        data = result.data if isinstance(result.data, dict) else {}
        tools = data.get("tools") if isinstance(data.get("tools"), list) else []
        result.data = tools
        return result

    note = f"{FALLBACK_NOTE} ({state.reason})"
    client = _fallback_client(server_command, env)
    try:
        client.initialize()
        tools = client.list_tools()
    finally:
        client.close()
    return InspectorResult(data=tools, exit_code=0, fallback=True, note=note)


def call_tool(
    server_command: list[str],
    env: dict[str, str],
    name: str,
    args: dict,
) -> InspectorResult:
    """``tools/call`` über den Inspector, sonst direkt über den MCP-Client."""
    state = availability()
    if state.ok:
        method_args = ["--method", "tools/call", "--tool-name", name]
        for key in sorted(args):
            value = json.dumps(args[key], ensure_ascii=False, separators=(",", ":"))
            method_args.extend(["--tool-arg", f"{key}={value}"])
        result = _run(server_command, env, method_args)
        if not isinstance(result.data, dict):
            result.data = {"isError": True, "content": [{"type": "text", "text": str(result.data)}]}
        return result

    note = f"{FALLBACK_NOTE} ({state.reason})"
    client = _fallback_client(server_command, env)
    try:
        client.initialize()
        response = client.call_tool(name, args)
    finally:
        client.close()
    if "error" in response:
        data = {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(response["error"], ensure_ascii=False),
                }
            ],
        }
        exit_code = 5
    else:
        data = response.get("result")
        if not isinstance(data, dict):
            data = {}
        exit_code = 5 if data.get("isError") else 0
    return InspectorResult(data=data, exit_code=exit_code, fallback=True, note=note)
