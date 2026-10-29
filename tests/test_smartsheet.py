"""Isolated source parser tests."""
import importlib.util
from pathlib import Path
import pytest
path = Path(__file__).parents[1] / "custom_components/lsbt/smartsheet.py"
spec = importlib.util.spec_from_file_location("lsbt_parser", path)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

CSV = "PM Route,First School,Minutes Late,Covering Bus,Second School,Minutes Late,Covering Bus\n17,CCA/LC/Daley,,,Wang,15,LT33\n"

def test_csv():
    result = parser.find_school(parser.parse_routes(CSV, "text/csv"), "17", "Wang")
    assert result["minutes_late"] == 15
    assert result["covering_bus"] == "LT33"

def test_blank_means_on_time():
    item = parser.find_school(parser.parse_routes(CSV, "text/csv"), "17", "CCA/LC/Daley")
    assert item["minutes_late"] == 0
    assert item["status"] == "on_time"

def test_html():
    html = "<table><tr><th>PM Route</th><th>First School</th><th>Minutes Late</th></tr><tr><td>7</td><td>Wang</td><td>12</td></tr></table>"
    assert parser.find_school(parser.parse_routes(html), "7", "Wang")["minutes_late"] == 12

def test_shell_fails():
    with pytest.raises(ValueError):
        parser.parse_routes("<html><div id='root'></div></html>")

def test_replacement_without_delay():
    row = "PM Route,First School,Minutes Late,Covering Bus\\n14,McAvinnue,,L21\\n".replace("\\n", "\n")
    item = parser.find_school(parser.parse_routes(row, "text/csv"), "14", "McAvinnue")
    assert item["minutes_late"] == 0
    assert item["status"] == "on_time"

def test_invalid_delay_not_treated_as_on_time():
    row = "PM Route,First School,Minutes Late\\n14,McAvinnue,unknown-delay\\n".replace("\\n", "\n")
    item = parser.find_school(parser.parse_routes(row, "text/csv"), "14", "McAvinnue")
    assert item["minutes_late"] is None
    assert item["status"] == "unknown"

def test_delayed_bus_can_also_have_covering_vehicle():
    row = "PM Route,First School,Minutes Late,Covering Bus\\n14,McAvinnue,15,L21\\n".replace("\\n", "\n")
    item = parser.find_school(parser.parse_routes(row, "text/csv"), "14", "McAvinnue")
    assert item["status"] == "delayed"
    assert item["minutes_late"] == 15
    assert item["covering_bus"] == "L21"


def test_missing_covering_bus_remains_blank_in_parser():
    item = parser.find_school(parser.parse_routes(CSV, "text/csv"), "17", "CCA/LC/Daley")
    assert item["covering_bus"] is None
    assert item["minutes_late"] == 0
    assert item["status"] == "on_time"
