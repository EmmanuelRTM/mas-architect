"""The shipped examples are the reference designs: they must lint clean."""

from mas_lint import lint
from mas_lint.loader import load_spec


def test_there_is_one_example_per_core_architecture(example_paths):
    assert len(example_paths) >= 5


def test_every_example_has_no_errors_or_warnings(example_paths):
    for path in example_paths:
        report = lint(load_spec(path))
        blocking = [f for f in report.findings if f.severity.value in ("error", "warning")]
        assert blocking == [], f"{path.name}: {[f.rule_id + ' ' + f.message for f in blocking]}"


def test_antipattern_fixture_trips_every_core_rule(antipattern_path):
    report = lint(load_spec(antipattern_path))
    found = {f.rule_id for f in report.findings}
    expected = {
        "MAS000", "MAS001", "MAS002", "MAS003", "MAS004", "MAS005", "MAS006",
        "MAS007", "MAS008", "MAS009", "MAS010", "MAS011", "MAS012", "MAS013",
        "MAS014", "MAS015", "MAS016", "MAS017", "MAS018", "MAS020", "MAS021",
    }
    assert expected <= found, sorted(expected - found)
    assert report.has_errors
