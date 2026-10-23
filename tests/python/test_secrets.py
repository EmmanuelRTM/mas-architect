"""Deterministic secret detection. Fake keys are built at run time so the
repository itself never holds a string that looks like a real credential."""

from mas_lint.secrets import find_secrets


def kinds(text):
    return {match.kind for match in find_secrets(text)}


def test_detects_anthropic_key():
    assert "anthropic-api-key" in kinds("key = " + "sk-ant-api03-" + "x" * 40)


def test_detects_aws_access_key():
    assert "aws-access-key-id" in kinds("AKIA" + "ABCDEFGHIJKLMNOP")


def test_detects_github_token():
    assert "github-token" in kinds("ghp_" + "a" * 36)


def test_detects_private_key_block():
    assert "private-key" in kinds("-----BEGIN " + "RSA PRIVATE KEY-----\nMIIE")


def test_detects_generic_assignment():
    assert "generic-secret-assignment" in kinds('api_key = "' + "Zq8" * 6 + '"')


def test_ignores_placeholders_and_env_references():
    text = "\n".join(
        [
            'api_key = "${ANTHROPIC_API_KEY}"',
            'token: "<your-token-here>"',
            'password = "changeme"',
            "secret = os.environ['SECRET']",
            'api_key = "your-api-key-goes-here"',
        ]
    )
    assert kinds(text) == set()


def test_match_never_carries_the_secret_value():
    fake = "ghp_" + "b" * 36
    match = find_secrets("token " + fake)[0]
    assert fake not in repr(match)
    assert match.line == 1
