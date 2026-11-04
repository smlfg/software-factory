import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
REPO = HARNESS.parents[1]
sys.path.insert(0, str(HARNESS))

from mcp_check import _mcp08_problems  # noqa: E402
MCP_CHECK = HARNESS / "mcp_check.py"
GOOD = HARNESS / "selftest" / "good_mcp"
BAD = HARNESS / "selftest" / "bad_mcp"
SCRATCH_TMP = REPO / "scratch" / "tmp"


def _workdir() -> Path:
    SCRATCH_TMP.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="mcp-check-selftest-", dir=SCRATCH_TMP))


def _run_check(repo: Path):
    root = _workdir()
    report = root / "report.md"
    command = [
        sys.executable,
        str(MCP_CHECK),
        str(repo),
        "--venv",
        str(root / "venv"),
        "--report",
        str(report),
    ]
    result = subprocess.run(
        command,
        cwd=str(REPO),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )
    text = report.read_text(encoding="utf-8") if report.is_file() else result.stdout
    return result.returncode, result.stdout, text


def _rows(report: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in report.splitlines():
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) >= 3 and parts[0].startswith("MCP"):
            rows[parts[0]] = parts[1]
    return rows


def test_good_mcp_passes():
    code, stdout, report = _run_check(GOOD)
    rows = _rows(report)
    assert code == 0, stdout
    assert "FAIL" not in rows.values(), report
    for check in (
        "MCP00",
        "MCP01",
        "MCP02",
        "MCP03",
        "MCP04",
        "MCP05",
        "MCP07",
        "MCP08",
    ):
        assert rows.get(check) == "PASS", f"{check} sollte PASS sein:\n{report}"
    assert rows.get("MCP06") in {"PASS", "SKIP"}, report


def test_bad_mcp_fails_expected_checks():
    code, stdout, report = _run_check(BAD)
    rows = _rows(report)
    assert code != 0, stdout
    for check in (
        "MCP00",
        "MCP01",
        "MCP02",
        "MCP04",
        "MCP05",
        "MCP06",
        "MCP07",
        "MCP08",
    ):
        assert rows.get(check) == "FAIL", f"{check} sollte FAIL sein:\n{report}"
    assert "stray stdout" in report
    assert "Traceback" in report
    assert "Secret-Leak" in report


def _tool(
    name="search_items",
    description="Searches the catalog for items. Use when the user wants to find something.",
    properties=None,
    annotations=None,
):
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties
            if properties is not None
            else {"query": {"type": "string", "description": "Search term"}},
        },
        "annotations": annotations
        if annotations is not None
        else {"readOnlyHint": True, "destructiveHint": False},
    }


def test_mcp08_accepts_complete_tool():
    problems, coverage = _mcp08_problems([_tool()])
    assert problems == []
    assert coverage == 100


def test_mcp08_reports_missing_parameter_description():
    tool = _tool(properties={"query": {"type": "string"}})
    problems, coverage = _mcp08_problems([tool])
    assert any("search_items.query" in problem for problem in problems)
    assert coverage == 0


def test_mcp08_reports_missing_annotation_hints():
    tool = _tool(annotations={"readOnlyHint": True})
    problems, coverage = _mcp08_problems([tool])
    assert not any("readOnlyHint" in problem for problem in problems)
    assert any("destructiveHint" in problem for problem in problems)
    assert coverage == 100


def test_mcp08_reports_contradictory_annotation_hints():
    tool = _tool(annotations={"readOnlyHint": True, "destructiveHint": True})
    problems, _ = _mcp08_problems([tool])
    assert any("widersprechen" in problem for problem in problems)


def test_mcp08_requires_usage_guidance_for_multiple_tools():
    first = _tool(name="search_items", description="Searches the catalog for matching items by keyword.")
    second = _tool(name="get_item", description="Returns the details of one catalog item by its identifier.")
    problems, _ = _mcp08_problems([first, second])
    assert sum("Abgrenzung fehlt" in problem for problem in problems) == 2


def test_mcp08_does_not_require_usage_guidance_for_single_tool():
    tool = _tool(description="Searches the catalog for matching items by keyword.")
    problems, _ = _mcp08_problems([tool])
    assert problems == []
