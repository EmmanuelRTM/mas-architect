import json

from mas_lint import lint
from mas_lint.formatting import format_text
from mas_lint.loader import load_spec
from mas_lint.practices import PRACTICES


def test_ten_practices_plus_ops():
    ids = [p.id for p in PRACTICES]
    assert ids[:10] == [f"P{i}" for i in range(1, 11)]
    assert "OPS" in ids
    assert "MOD" in ids


def test_practice_status_reflects_findings(antipattern_path, base_spec):
    bad = lint(load_spec(antipattern_path)).to_dict()["practices"]
    assert bad["P1"] == "fail"
    assert bad["P3"] == "warn"
    good = lint(base_spec).to_dict()["practices"]
    assert good["P1"] == "pass"
    assert good["P10"] == "n/a"


def test_report_is_json_serialisable(base_spec):
    data = json.loads(json.dumps(lint(base_spec).to_dict()))
    assert data["spec"] == "verifiable-qa-pool"
    assert data["summary"] == {"error": 0, "warning": 0, "info": data["summary"]["info"]}
    assert "metrics" in data


def test_text_format_lists_rule_ids(antipattern_path):
    text = format_text(lint(load_spec(antipattern_path)))
    assert "MAS001" in text
    assert "error" in text.lower()


def test_report_exposes_monitoring_and_platform(base_spec):
    data = lint(base_spec).to_dict()
    assert data["monitoring"] == base_spec["monitoring"]
    assert data["platform"] == base_spec["platform"]
    del base_spec["monitoring"], base_spec["platform"]
    data = lint(base_spec).to_dict()
    assert data["monitoring"] == {} and data["platform"] == {}
