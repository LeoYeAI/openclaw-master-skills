import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import novada_search as ns
import novada_mcp_server as mcp


def test_research_method_exists():
    assert hasattr(ns.NovadaSearch, 'research')


def test_research_docstring():
    doc = ns.NovadaSearch.research.__doc__ or ""
    assert "search" in doc.lower()


def test_research_cli_mode_present():
    src = (ROOT / 'novada_search.py').read_text()
    assert '"research"' in src


def test_research_mcp_tool_present():
    names = [t['name'] for t in mcp.handle_tools_list()['tools']]
    assert 'novada_research' in names
