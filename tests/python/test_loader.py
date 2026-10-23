import json

import pytest

from mas_lint.loader import SpecLoadError, load_spec, loads_spec


def test_loads_json_object(tmp_path):
    path = tmp_path / "team.mas.json"
    path.write_text(json.dumps({"name": "x"}))
    assert load_spec(path) == {"name": "x"}


def test_invalid_json_raises_with_location(tmp_path):
    path = tmp_path / "broken.mas.json"
    path.write_text('{"name": ')
    with pytest.raises(SpecLoadError) as info:
        load_spec(path)
    assert "line" in str(info.value)


def test_top_level_must_be_object():
    with pytest.raises(SpecLoadError):
        loads_spec("[1, 2]", suffix=".json")


def test_missing_file_raises(tmp_path):
    with pytest.raises(SpecLoadError):
        load_spec(tmp_path / "nope.mas.json")


def test_yaml_spec_when_pyyaml_is_available(tmp_path):
    pytest.importorskip("yaml")
    path = tmp_path / "team.mas.yaml"
    path.write_text("name: from-yaml\nagents: []\n")
    assert load_spec(path)["name"] == "from-yaml"
